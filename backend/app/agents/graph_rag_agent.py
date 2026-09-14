"""
Graph-RAG Agent for FlyConnectome AI (Phase 4).
Executes mathematically verified graph traversals on the connectome multigraph,
computes multi-factor relevance scores, extracts 3D subgraphs, formats LLM prompt context,
and runs in-silico ablation.
"""

from typing import Dict, List, Any, Optional
from ..graph.engine import graph_engine
from ..graph_rag import (
    GraphRAGQueryRequest,
    graph_rag_retriever,
    GraphRAGRetriever,
)


class GraphRAGAgent:
    def __init__(self, retriever: Optional[GraphRAGRetriever] = None):
        self.name = "Connectome Graph-RAG & Traversal Agent"
        self.retriever = retriever or graph_rag_retriever

    def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute graph operations and retrieval based on the planner's specifications.
        Returns scored pathways, 3D subgraph packaging, LLM prompt context, and ablation results.
        """
        sources = plan.get("source_neuron_ids", [])
        targets = plan.get("target_neuron_ids", [])
        ablation_targets = plan.get("ablation_target_ids", [])
        is_ablation = plan.get("is_ablation_requested", False)
        query = plan.get("query", plan.get("research_question", "Connectome circuit traversal"))

        thought_steps = []
        thought_steps.append(f"Executing Graph-RAG retrieval pipeline from {len(sources)} source candidate(s) to {len(targets)} target(s).")

        # 1. Execute Graph-RAG Retrieval with multi-factor scoring
        rag_req = GraphRAGQueryRequest(
            query=query,
            source_neuron_ids=sources,
            target_neuron_ids=targets,
            neuropil_rois=plan.get("target_rois", []),
            neurotransmitters=plan.get("target_neurotransmitters", []),
            max_depth=5,
            min_synapses=5,
            max_pathways=8,
            token_budget=2500,
            include_markdown_context=True,
        )
        rag_response = self.retriever.retrieve(rag_req)

        paths = []
        for p in rag_response.ranked_pathways:
            path_steps = []
            for u, v in zip(p.node_ids[:-1], p.node_ids[1:]):
                w = graph_engine.graph[u][v].get("weight", 1) if graph_engine.graph.has_edge(u, v) else 1
                u_n = graph_engine.get_neuron(u)
                v_n = graph_engine.get_neuron(v)
                path_steps.append({
                    "from_id": u,
                    "from_name": u_n.get("name", u) if u_n else u,
                    "to_id": v,
                    "to_name": v_n.get("name", v) if v_n else v,
                    "synapses": w,
                    "type": "chemical",
                })

            paths.append({
                "path_id": p.path_id,
                "node_ids": p.node_ids,
                "node_names": p.node_names,
                "total_synapses": p.total_synapses,
                "biological_distance": p.biological_distance,
                "bottleneck_synapses": p.bottleneck_synapses,
                "bottleneck_edge": p.bottleneck_edge,
                "hops": max(1, len(p.node_ids) - 1),
                "steps": path_steps,
                "relevance_score": p.score.composite_score,
                "score_breakdown": p.score.model_dump(),
            })

        subgraph = {
            "nodes": [n.model_dump() for n in rag_response.nodes],
            "edges": [e.model_dump() for e in rag_response.edges],
        }

        # Calculate bottlenecks from graph engine
        circuit_res = graph_engine.find_circuit_pathways(
            source_ids=sources,
            target_ids=targets,
            max_depth=5,
            cutoff_paths=8
        )
        bottlenecks = circuit_res.get("bottlenecks", [])

        thought_steps.append(
            f"Discovered {len(paths)} synaptic pathway(s) spanning {len(subgraph['nodes'])} neurons "
            f"and {len(subgraph['edges'])} synaptic connections."
        )

        if paths:
            strongest_path = paths[0]
            names_chain = " → ".join(strongest_path["node_names"])
            rel = strongest_path["relevance_score"]
            thought_steps.append(
                f"Top-ranked pathway: {names_chain} (relevance: {rel:.4f}, {strongest_path['total_synapses']} synapses)."
            )

        if bottlenecks:
            b_names = [b["name"] for b in bottlenecks[:2]]
            thought_steps.append(f"Calculated flow bottlenecks via betweenness centrality: {', '.join(b_names)}.")

        # 2. In-Silico Ablation Simulation
        ablation_res = None
        if is_ablation and ablation_targets:
            thought_steps.append(f"Initiating in-silico ablation simulation for target neuron(s): {ablation_targets}...")
            ablation_res = graph_engine.simulate_ablation(
                silenced_ids=ablation_targets,
                source_ids=sources,
                target_ids=targets
            )
            thought_steps.append(
                f"Ablation evaluation complete: {ablation_res['severance_percentage']}% circuit severance. "
                f"Throughput loss: {ablation_res['throughput_loss_percentage']}%. Vulnerability Score: {ablation_res['vulnerability_score']}/10."
            )

        return {
            "paths": paths,
            "subgraph": subgraph,
            "bottlenecks": bottlenecks,
            "ablation": ablation_res,
            "sources": rag_response.grounded_entities.get("sources", sources),
            "targets": rag_response.grounded_entities.get("targets", targets),
            "total_pathways_found": len(paths),
            "rag_context": rag_response.context.markdown_context,
            "rag_summary": rag_response.context.dense_graph_summary,
            "tier_a_provenance": rag_response.context.tier_a_provenance,
            "thought_log": thought_steps
        }


graph_rag_agent = GraphRAGAgent()

