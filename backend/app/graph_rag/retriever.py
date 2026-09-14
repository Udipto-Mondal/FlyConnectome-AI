"""
Graph-RAG Retriever Engine for FlyConnectome AI (Phase 4).
Orchestrates natural language entity grounding, connectome multigraph traversals,
multi-factor circuit relevance scoring, and anti-hallucination LLM context compilation.
"""

import time
import uuid
from typing import List, Dict, Any, Optional, Set

from .models import (
    GraphRAGQueryRequest,
    GraphRAGRetrievalResponse,
    ScoredPathway,
    GraphRAGContext,
)
from .scorer import circuit_scorer, CircuitRelevanceScorer
from .formatter import context_formatter, ConnectomeContextFormatter
from ..graph.engine import graph_engine, ConnectomeGraphEngine
from ..graph.models import (
    PathSearchRequest,
    SubgraphExtractionRequest,
    ComputationalProvenanceRecord,
    SubgraphNode,
    SubgraphEdge,
)
from ..connectome.query_layer import ConnectomeQueryLayer


class GraphRAGRetriever:
    """
    High-level Graph-RAG Retrieval Engine bridging the Drosophila Male CNS connectome
    with LLM reasoning agents.
    """

    def __init__(
        self,
        engine: Optional[ConnectomeGraphEngine] = None,
        query_layer: Optional[ConnectomeQueryLayer] = None,
        scorer: Optional[CircuitRelevanceScorer] = None,
        formatter: Optional[ConnectomeContextFormatter] = None,
    ):
        self.engine = engine or graph_engine
        self.query_layer = query_layer or ConnectomeQueryLayer()
        self.scorer = scorer or circuit_scorer
        self.formatter = formatter or context_formatter

    def ground_entities(
        self,
        query: str,
        seed_ids: Optional[List[str]] = None,
        source_ids: Optional[List[str]] = None,
        target_ids: Optional[List[str]] = None,
        rois: Optional[List[str]] = None,
        neurotransmitters: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Resolve neuroscience query tokens, cell types, and ROI spatial tags into
        grounded Janelia body IDs and neuron metadata.
        """
        grounded_sources: Set[str] = set()
        grounded_targets: Set[str] = set()
        grounded_seeds: Set[str] = set()
        recognized_keywords: List[str] = []

        # 1. Add explicitly provided IDs
        if source_ids:
            grounded_sources.update(self.engine.resolve_neuron_ids(source_ids))
        if target_ids:
            grounded_targets.update(self.engine.resolve_neuron_ids(target_ids))
        if seed_ids:
            grounded_seeds.update(self.engine.resolve_neuron_ids(seed_ids))

        # 2. Extract potential entities from natural language query
        query_clean = query.strip().lower()

        # Check known neuron types and names in local dictionary
        for neuron_id, n_data in self.engine.neuron_lookup.items():
            name = str(n_data.get("name", "")).lower()
            ntype = str(n_data.get("type", "")).lower()
            instance = str(n_data.get("instance", "")).lower()

            if (name and name in query_clean) or (ntype and ntype in query_clean) or (instance and instance in query_clean):
                recognized_keywords.append(name or ntype)
                # Assign to source or target based on sensory/motor heuristics
                if any(term in ntype for term in ["visual", "sensory", "projection", "lc", "input"]):
                    grounded_sources.add(neuron_id)
                elif any(term in ntype for term in ["motor", "descending", "mn", "output"]):
                    grounded_targets.add(neuron_id)
                else:
                    grounded_seeds.add(neuron_id)

        # 3. If sources or targets are still empty, derive sensible defaults from seeds or search
        if not grounded_sources and not grounded_targets:
            # Fallback search across engine
            matches = self.engine.search_neurons(query)
            if matches:
                for m in matches[:4]:
                    grounded_seeds.add(str(m["id"]))

        # Check if query specifically asks for Giant Fiber escape circuit
        if any(k in query_clean for k in ["giant fiber", "escape", "jump", "visual"]):
            gf_ids = self.engine.resolve_neuron_ids(["GF_L", "10234", "LC4_L"])
            grounded_sources.update([gid for gid in gf_ids if "10005" in gid or "lc4" in gid.lower()])
            grounded_targets.update([gid for gid in gf_ids if "10234" in gid or "gf" in gid.lower()])
            if not grounded_sources:
                grounded_sources.update(self.engine.resolve_neuron_ids(["LC4_L", "10005"]))
            if not grounded_targets:
                grounded_targets.update(self.engine.resolve_neuron_ids(["GF_L", "10234"]))

        # Deduplicate and sort
        final_sources = sorted(list(grounded_sources))
        final_targets = sorted(list(grounded_targets))
        final_seeds = sorted(list(grounded_seeds))

        return {
            "sources": final_sources,
            "targets": final_targets,
            "seeds": final_seeds,
            "matched_keywords": list(set(recognized_keywords)),
            "applied_rois": rois or [],
            "applied_neurotransmitters": neurotransmitters or [],
        }

    def retrieve(self, request: GraphRAGQueryRequest) -> GraphRAGRetrievalResponse:
        """
        Execute full Graph-RAG retrieval pipeline:
        Query -> Grounding -> Subgraph Extraction -> Multi-Factor Scoring -> LLM Context Compilation.
        """
        start_time = time.time()

        # Step 1: Biological Entity Grounding
        grounded = self.ground_entities(
            query=request.query,
            seed_ids=request.seed_neuron_ids,
            source_ids=request.source_neuron_ids,
            target_ids=request.target_neuron_ids,
            rois=request.neuropil_rois,
            neurotransmitters=request.neurotransmitters,
        )

        sources = grounded["sources"]
        targets = grounded["targets"]
        seeds = grounded["seeds"]

        # Step 2: Multi-Hop Pathway Traversal
        raw_paths: List[Dict[str, Any]] = []
        if sources and targets:
            path_req = PathSearchRequest(
                source_ids=sources,
                target_ids=targets,
                max_depth=request.max_depth,
                min_synapses=request.min_synapses,
                max_paths=max(request.max_pathways * 2, 10),
                algorithm="all_simple",
            )
            path_res = self.engine.find_pathways_v2(path_req)
            raw_paths = [p.model_dump() for p in path_res.paths]
        elif sources or targets or seeds:
            # If only unilateral endpoints available, extract 1-hop partners
            active_ids = sources or targets or seeds
            for nid in active_ids[:5]:
                if self.engine.graph.has_node(nid):
                    for succ in self.engine.graph.successors(nid):
                        w = self.engine.graph[nid][succ].get("weight", 0)
                        if w >= request.min_synapses:
                            n_src = self.engine.get_neuron(nid) or {"id": nid, "name": nid}
                            n_dst = self.engine.get_neuron(succ) or {"id": succ, "name": succ}
                            raw_paths.append({
                                "node_ids": [nid, succ],
                                "node_names": [n_src.get("name", nid), n_dst.get("name", succ)],
                                "total_synapses": w,
                                "biological_distance": round(1000.0 / max(1, w), 2),
                                "bottleneck_synapses": w,
                                "bottleneck_edge": [nid, succ],
                            })

        # Step 3: Multi-Factor Relevance Scoring
        scored_pathways: List[ScoredPathway] = []
        betweenness_cache: Dict[str, float] = {}
        try:
            betweenness_cache = nx.betweenness_centrality(self.engine.graph, weight="weight", normalized=True)
        except Exception:
            pass

        for p_idx, p in enumerate(raw_paths):
            p_node_ids = [str(x) for x in p["node_ids"]]
            p_node_names = [str(x) for x in p.get("node_names", p_node_ids)]
            total_syn = int(p.get("total_synapses", 0))
            bio_dist = float(p.get("biological_distance", 0.0))
            bottle_syn = int(p.get("bottleneck_synapses", total_syn))
            bottle_edge = p.get("bottleneck_edge")

            score_bd = self.scorer.score_pathway(
                node_ids=p_node_ids,
                node_names=p_node_names,
                total_synapses=total_syn,
                biological_distance=bio_dist,
                bottleneck_synapses=bottle_syn,
                graph=self.engine.graph,
                node_metadata=self.engine.neuron_lookup,
                query=request.query,
                target_rois=request.neuropil_rois,
                target_neurotransmitters=request.neurotransmitters,
                betweenness_cache=betweenness_cache,
            )

            scored_pathways.append(
                ScoredPathway(
                    path_id=f"path_{uuid.uuid4().hex[:8]}",
                    node_ids=p_node_ids,
                    node_names=p_node_names,
                    total_synapses=total_syn,
                    biological_distance=bio_dist,
                    bottleneck_synapses=bottle_syn,
                    bottleneck_edge=bottle_edge,
                    score=score_bd,
                )
            )

        # Sort ranked pathways by composite score descending
        scored_pathways.sort(key=lambda sp: sp.score.composite_score, reverse=True)
        top_ranked_pathways = scored_pathways[:request.max_pathways]

        # Step 4: Extract Induced Subgraph for Context & Visualization
        participating_node_ids: Set[str] = set(sources + targets + seeds)
        for sp in top_ranked_pathways:
            participating_node_ids.update(sp.node_ids)

        if not participating_node_ids:
            # Fallback to general showcase nodes if graph query returned zero matches
            participating_node_ids.update(list(self.engine.neuron_lookup.keys())[:8])

        subgraph_req = SubgraphExtractionRequest(
            node_ids=list(participating_node_ids),
            expand_hops=1,
            min_synapses=request.min_synapses,
            include_3d_coordinates=True,
        )
        subgraph_res = self.engine.extract_subgraph_v2(subgraph_req)

        # Step 5: Format LLM RAG Context
        formatted_context: GraphRAGContext
        if request.include_markdown_context:
            formatted_context = self.formatter.format_context(
                nodes=subgraph_res.nodes,
                edges=subgraph_res.edges,
                ranked_pathways=top_ranked_pathways,
                query=request.query,
                token_budget=request.token_budget,
            )
        else:
            formatted_context = GraphRAGContext(
                markdown_context="",
                dense_graph_summary={},
                total_nodes=len(subgraph_res.nodes),
                total_edges=len(subgraph_res.edges),
                token_count_estimate=0,
                tier_a_provenance=[],
            )

        # Tier C computational execution provenance
        latency = round((time.time() - start_time) * 1000, 2)
        provenance = ComputationalProvenanceRecord(
            provenance_id=f"prov_rag_{uuid.uuid4().hex[:8]}",
            algorithm="graph_rag_retrieval_v1",
            node_count=len(subgraph_res.nodes),
            edge_count=len(subgraph_res.edges),
            latency_ms=latency,
            parameters={
                "query": request.query,
                "sources_count": len(sources),
                "targets_count": len(targets),
                "max_depth": request.max_depth,
                "min_synapses": request.min_synapses,
                "token_budget": request.token_budget,
            },
        )

        return GraphRAGRetrievalResponse(
            query=request.query,
            grounded_entities=grounded,
            nodes=subgraph_res.nodes,
            edges=subgraph_res.edges,
            ranked_pathways=top_ranked_pathways,
            context=formatted_context,
            provenance=provenance,
        )


graph_rag_retriever = GraphRAGRetriever()
