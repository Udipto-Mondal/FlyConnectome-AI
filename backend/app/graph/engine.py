"""
Connectome Graph Engine for NeuroGraph AI (Phase 3).
NetworkX-powered directed graph traversal engine providing:
- Inverted biological resistance weight formulation for Dijkstra pathfinding
- Directed K-hop traversals and multi-path ranking
- Betweenness bottleneck centrality, Closeness, PageRank, and Synaptic Degree
- In-silico circuit ablation adhering to docs/architecture.md Section 5
- Subgraph extraction formatted for 2D/3D WebGL rendering
- Global topological invariant calculations and Tier C computational provenance
"""

import time
import uuid
from typing import Dict, List, Optional, Any, Set, Tuple
import networkx as nx

from .connectome_data import NEURON_DATABASE, SYNAPTIC_CONNECTIONS, SHOWCASE_PRESETS
from .models import (
    PathStep,
    CircuitPathway,
    PathSearchRequest,
    PathSearchResponse,
    CentralityRequest,
    CentralityResponse,
    NodeCentrality,
    SubgraphExtractionRequest,
    SubgraphExtractionResponse,
    SubgraphNode,
    SubgraphEdge,
    AblationRequestV2,
    AblationResponseV2,
    GraphTopologyResponse,
    ComputationalProvenanceRecord,
)


class ConnectomeGraphEngine:
    """
    Core graph algorithms engine for Drosophila Male CNS connectome circuits.
    """

    def __init__(self, custom_neurons: Optional[List[Dict[str, Any]]] = None, custom_connections: Optional[List[Dict[str, Any]]] = None):
        self.graph = nx.DiGraph()
        self.neuron_lookup: Dict[str, Dict[str, Any]] = {}
        self.name_to_id: Dict[str, str] = {}
        self._build_graph(custom_neurons, custom_connections)

    def _build_graph(self, custom_neurons: Optional[List[Dict[str, Any]]] = None, custom_connections: Optional[List[Dict[str, Any]]] = None):
        """
        Build directed multigraph with biological attributes and inverted weights for Dijkstra.
        Distance formulation: d(u, v) = 1000.0 / max(1, w_synapses)
        """
        neurons = custom_neurons if custom_neurons is not None else NEURON_DATABASE
        connections = custom_connections if custom_connections is not None else SYNAPTIC_CONNECTIONS

        self.graph.clear()
        self.neuron_lookup.clear()
        self.name_to_id.clear()

        for neuron in neurons:
            n_id = str(neuron.get("id") or neuron.get("body_id"))
            name = neuron.get("name") or neuron.get("instance") or f"Neuron_{n_id}"
            
            # Normalize neuron dict
            normalized = {
                "id": n_id,
                "name": name,
                "type": neuron.get("type"),
                "neuropil": neuron.get("neuropil") or neuron.get("soma_neuropil"),
                "subsystem": neuron.get("subsystem", "General"),
                "neurotransmitter": neuron.get("neurotransmitter"),
                "description": neuron.get("description", ""),
                "coords": neuron.get("coords") or [0.0, 0.0, 0.0],
                "sex_dimorphic": neuron.get("sex_dimorphic", False),
            }
            self.neuron_lookup[n_id] = normalized
            self.name_to_id[name.lower()] = n_id

            self.graph.add_node(
                n_id,
                name=normalized["name"],
                type=normalized["type"],
                neuropil=normalized["neuropil"],
                subsystem=normalized["subsystem"],
                neurotransmitter=normalized["neurotransmitter"],
                description=normalized["description"],
                coords=normalized["coords"],
                sex_dimorphic=normalized["sex_dimorphic"],
            )

        for edge in connections:
            src = str(edge.get("source") or edge.get("pre_body_id"))
            tgt = str(edge.get("target") or edge.get("post_body_id"))
            synapses = int(edge.get("synapses") or edge.get("weight", 1))
            edge_type = edge.get("type", "chemical")
            roi = edge.get("roi")

            # Biological distance: Higher synaptic count = lower resistance = shorter distance
            dist_weight = max(0.1, 1000.0 / float(max(1, synapses)))

            self.graph.add_edge(
                src,
                tgt,
                synapses=synapses,
                type=edge_type,
                roi=roi,
                weight=dist_weight
            )

    def search_neurons(self, query: str) -> List[Dict[str, Any]]:
        """Search neurons by name, type, neuropil, subsystem, or ID."""
        q = query.lower().strip()
        results = []
        for n_id, neuron in self.neuron_lookup.items():
            if (
                q in neuron["name"].lower()
                or (neuron.get("type") and q in neuron["type"].lower())
                or (neuron.get("neuropil") and q in neuron["neuropil"].lower())
                or (neuron.get("subsystem") and q in neuron["subsystem"].lower())
                or (neuron.get("description") and q in neuron["description"].lower())
                or q == n_id
            ):
                results.append(neuron)
        return results

    def get_neuron(self, neuron_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve metadata for a specific neuron by ID."""
        return self.neuron_lookup.get(str(neuron_id))

    def resolve_neuron_ids(self, names_or_ids: List[str]) -> List[str]:
        """Convert a list of names, partial names, or IDs into valid neuron IDs."""
        resolved = []
        for item in names_or_ids:
            s = str(item).strip()
            if s in self.neuron_lookup:
                resolved.append(s)
                continue
            lower_s = s.lower()
            if lower_s in self.name_to_id:
                resolved.append(self.name_to_id[lower_s])
                continue
            matches = self.search_neurons(s)
            if matches:
                resolved.append(str(matches[0]["id"]))
        return list(dict.fromkeys(resolved))

    # =========================================================================
    # Phase 3: High-Performance Pathfinding & Dijkstra Traversals
    # =========================================================================

    def find_pathways_v2(self, request: PathSearchRequest) -> PathSearchResponse:
        """
        Phase 3 Path Search Engine:
        Finds direct and polysynaptic pathways between sources and targets.
        Supports:
        - Dijkstra weighted shortest paths (inverted biological resistance)
        - All simple paths filtered by synaptic thresholds and depth
        - Bottleneck calculation and Tier C provenance tracking
        """
        start_time = time.time()
        resolved_sources = self.resolve_neuron_ids(request.source_ids)
        resolved_targets = self.resolve_neuron_ids(request.target_ids)

        if not resolved_sources or not resolved_targets:
            latency = round((time.time() - start_time) * 1000, 2)
            prov = ComputationalProvenanceRecord(
                provenance_id=f"prov_path_{uuid.uuid4().hex[:8]}",
                algorithm=f"path_search_{request.algorithm}",
                node_count=self.graph.number_of_nodes(),
                edge_count=self.graph.number_of_edges(),
                latency_ms=latency,
                parameters=request.model_dump(),
            )
            return PathSearchResponse(
                paths=[],
                total_pathways_found=0,
                sources=[],
                targets=[],
                bottlenecks=[],
                provenance=prov,
            )

        candidate_paths: List[List[str]] = []

        for src in resolved_sources:
            for tgt in resolved_targets:
                if src == tgt or not (self.graph.has_node(src) and self.graph.has_node(tgt)):
                    continue

                if request.algorithm.lower() == "dijkstra":
                    # Dijkstra shortest path based on inverted biological resistance
                    try:
                        if nx.has_path(self.graph, src, tgt):
                            d_path = nx.shortest_path(self.graph, source=src, target=tgt, weight="weight")
                            if len(d_path) - 1 <= request.max_depth:
                                candidate_paths.append(d_path)
                            # Also check if alternative shortest paths exist
                            all_d = list(nx.all_shortest_paths(self.graph, source=src, target=tgt, weight="weight"))
                            for alt_path in all_d:
                                if alt_path not in candidate_paths and len(alt_path) - 1 <= request.max_depth:
                                    candidate_paths.append(alt_path)
                    except (nx.NetworkXNoPath, nx.NodeNotFound):
                        pass
                else:
                    # All simple paths with depth cutoff
                    try:
                        simple_paths = list(nx.all_simple_paths(self.graph, source=src, target=tgt, cutoff=request.max_depth))
                        candidate_paths.extend(simple_paths)
                    except (nx.NetworkXNoPath, nx.NodeNotFound):
                        pass

        # De-duplicate candidate paths
        unique_paths: List[List[str]] = []
        seen_paths = set()
        for p in candidate_paths:
            p_tuple = tuple(p)
            if p_tuple not in seen_paths:
                seen_paths.add(p_tuple)
                unique_paths.append(p)

        # Build structured CircuitPathway objects
        path_objects: List[CircuitPathway] = []
        participating_nodes: Set[str] = set()

        for path in unique_paths:
            # Check min synapses constraint
            valid = True
            steps: List[PathStep] = []
            total_synapses = 0
            bottleneck = float("inf")
            cumulative_dist = 0.0

            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edata = self.graph[u][v]
                synapses = edata["synapses"]
                if synapses < request.min_synapses:
                    valid = False
                    break
                dist = edata.get("weight", max(0.1, 1000.0 / float(synapses)))
                steps.append(
                    PathStep(
                        from_id=u,
                        from_name=self.neuron_lookup.get(u, {}).get("name", u),
                        to_id=v,
                        to_name=self.neuron_lookup.get(v, {}).get("name", v),
                        synapses=synapses,
                        biological_distance=round(dist, 2),
                        type=edata.get("type", "chemical"),
                        roi=edata.get("roi"),
                    )
                )
                total_synapses += synapses
                bottleneck = min(bottleneck, synapses)
                cumulative_dist += dist

            if not valid:
                continue

            nodes_info = [self.neuron_lookup[nid] for nid in path if nid in self.neuron_lookup]
            node_names = [n["name"] for n in nodes_info]
            participating_nodes.update(path)

            path_objects.append(
                CircuitPathway(
                    nodes=nodes_info,
                    node_names=node_names,
                    node_ids=path,
                    steps=steps,
                    total_synapses=total_synapses,
                    bottleneck_synapses=int(bottleneck if bottleneck != float("inf") else 0),
                    cumulative_biological_distance=round(cumulative_dist, 2),
                    hops=len(path) - 1,
                )
            )

        # Sort paths according to user preference
        if request.weight_metric == "biological_distance":
            # Lowest biological resistance first
            path_objects.sort(key=lambda x: (x.cumulative_biological_distance, -x.bottleneck_synapses))
        else:
            # Highest synaptic strength first
            path_objects.sort(key=lambda x: (-x.total_synapses, -x.bottleneck_synapses))

        selected_paths = path_objects[:request.cutoff_paths]

        # Calculate bottleneck nodes using betweenness centrality on the participating subgraph
        bottlenecks = []
        if len(participating_nodes) > 2:
            sub_g = self.graph.subgraph(participating_nodes)
            cent = nx.betweenness_centrality(sub_g, weight="weight")
            for nid, score in sorted(cent.items(), key=lambda x: x[1], reverse=True):
                if score > 0.05 and nid not in resolved_sources and nid not in resolved_targets:
                    n_info = self.neuron_lookup.get(nid)
                    if n_info:
                        bottlenecks.append({
                            "id": nid,
                            "name": n_info["name"],
                            "type": n_info.get("type"),
                            "neuropil": n_info.get("neuropil"),
                            "centrality_score": round(score, 4),
                        })

        latency = round((time.time() - start_time) * 1000, 2)
        prov = ComputationalProvenanceRecord(
            provenance_id=f"prov_path_{uuid.uuid4().hex[:8]}",
            algorithm=f"path_search_{request.algorithm}",
            node_count=len(participating_nodes) or self.graph.number_of_nodes(),
            edge_count=sum(p.hops for p in selected_paths),
            latency_ms=latency,
            parameters=request.model_dump(),
        )

        return PathSearchResponse(
            paths=selected_paths,
            total_pathways_found=len(path_objects),
            sources=[self.neuron_lookup[s] for s in resolved_sources if s in self.neuron_lookup],
            targets=[self.neuron_lookup[t] for t in resolved_targets if t in self.neuron_lookup],
            bottlenecks=bottlenecks,
            provenance=prov,
        )

    # Legacy wrapper for backward compatibility with Phase 0/1/2 tests
    def find_circuit_pathways(
        self,
        source_ids: List[str],
        target_ids: List[str],
        max_depth: int = 5,
        cutoff_paths: int = 8
    ) -> Dict[str, Any]:
        """Backward-compatible pathway discovery wrapper for Phase 0/1/2 tests."""
        req = PathSearchRequest(
            source_ids=source_ids,
            target_ids=target_ids,
            algorithm="all_simple",
            max_depth=max_depth,
            cutoff_paths=cutoff_paths,
            weight_metric="synapses"
        )
        resp = self.find_pathways_v2(req)
        subgraph = self.extract_subgraph([n for p in resp.paths for n in p.node_ids])

        formatted_paths = []
        for p in resp.paths:
            steps = [
                {
                    "from_name": s.from_name,
                    "to_name": s.to_name,
                    "synapses": s.synapses,
                    "type": s.type
                }
                for s in p.steps
            ]
            formatted_paths.append({
                "nodes": p.nodes,
                "node_names": p.node_names,
                "steps": steps,
                "total_synapses": p.total_synapses,
                "hops": p.hops
            })

        return {
            "paths": formatted_paths,
            "subgraph": subgraph,
            "bottlenecks": resp.bottlenecks,
            "sources": resp.sources,
            "targets": resp.targets,
            "total_pathways_found": resp.total_pathways_found
        }

    # =========================================================================
    # Phase 3: Centrality & Bottleneck Hub Analytics
    # =========================================================================

    def compute_centrality_v2(self, request: CentralityRequest) -> CentralityResponse:
        """
        Compute node centrality metrics (Betweenness, Closeness, PageRank, Degree).
        """
        start_time = time.time()
        target_graph = self.graph

        if request.node_ids:
            resolved_ids = self.resolve_neuron_ids(request.node_ids)
            if resolved_ids:
                target_graph = self.graph.subgraph(resolved_ids)

        nodes = list(target_graph.nodes())
        n_count = len(nodes)

        # 1. Betweenness Centrality
        betweenness = {}
        if "betweenness" in request.metrics and n_count > 2:
            betweenness = nx.betweenness_centrality(target_graph, weight="weight")

        # 2. Closeness Centrality
        closeness = {}
        if "closeness" in request.metrics and n_count > 1:
            closeness = nx.closeness_centrality(target_graph, distance="weight")

        # 3. PageRank (Directed Flow influence)
        pagerank = {}
        if "pagerank" in request.metrics and n_count > 0:
            try:
                pagerank = nx.pagerank(target_graph, weight="synapses", alpha=0.85, max_iter=100)
            except Exception:
                # Fallback unweighted
                pagerank = nx.pagerank(target_graph, alpha=0.85, max_iter=100)

        node_centrality_list: List[NodeCentrality] = []
        for nid in nodes:
            n_info = self.neuron_lookup.get(nid, {})
            in_deg = target_graph.in_degree(nid)
            out_deg = target_graph.out_degree(nid)
            in_syn = sum(target_graph[u][nid]["synapses"] for u in target_graph.predecessors(nid))
            out_syn = sum(target_graph[nid][v]["synapses"] for v in target_graph.successors(nid))

            b_score = round(betweenness.get(nid, 0.0), 4) if "betweenness" in request.metrics else None
            c_score = round(closeness.get(nid, 0.0), 4) if "closeness" in request.metrics else None
            p_score = round(pagerank.get(nid, 0.0), 4) if "pagerank" in request.metrics else None

            node_centrality_list.append(
                NodeCentrality(
                    node_id=nid,
                    name=n_info.get("name", nid),
                    type=n_info.get("type"),
                    neuropil=n_info.get("neuropil"),
                    betweenness_centrality=b_score,
                    closeness_centrality=c_score,
                    pagerank=p_score,
                    in_degree=in_deg,
                    out_degree=out_deg,
                    in_synapses=in_syn,
                    out_synapses=out_syn,
                )
            )

        # Top bottlenecks ranked by betweenness
        top_bottlenecks = sorted(
            [n for n in node_centrality_list if n.betweenness_centrality is not None],
            key=lambda x: x.betweenness_centrality or 0.0,
            reverse=True
        )[:10]

        latency = round((time.time() - start_time) * 1000, 2)
        prov = ComputationalProvenanceRecord(
            provenance_id=f"prov_cent_{uuid.uuid4().hex[:8]}",
            algorithm="network_centrality",
            node_count=n_count,
            edge_count=target_graph.number_of_edges(),
            latency_ms=latency,
            parameters=request.model_dump(),
        )

        return CentralityResponse(
            nodes=node_centrality_list,
            top_bottlenecks=top_bottlenecks,
            provenance=prov,
        )

    # =========================================================================
    # Phase 3: Subgraph Extraction & 3D Packaging
    # =========================================================================

    def extract_subgraph_v2(self, request: SubgraphExtractionRequest) -> SubgraphExtractionResponse:
        """
        Extract an induced circuit subgraph formatted for 2D/3D WebGL / Three.js visualization.
        """
        start_time = time.time()
        resolved_ids = self.resolve_neuron_ids(request.node_ids)
        selected_nodes = set(resolved_ids)

        if request.expand_hops > 0:
            frontier = set(resolved_ids)
            for _ in range(request.expand_hops):
                new_frontier = set()
                for nid in frontier:
                    if self.graph.has_node(nid):
                        new_frontier.update(self.graph.predecessors(nid))
                        new_frontier.update(self.graph.successors(nid))
                selected_nodes.update(new_frontier)
                frontier = new_frontier

        nodes_list: List[SubgraphNode] = []
        for nid in selected_nodes:
            if nid in self.neuron_lookup:
                n = self.neuron_lookup[nid]
                in_deg = self.graph.in_degree(nid) if self.graph.has_node(nid) else 0
                out_deg = self.graph.out_degree(nid) if self.graph.has_node(nid) else 0
                nodes_list.append(
                    SubgraphNode(
                        id=nid,
                        name=n["name"],
                        type=n.get("type"),
                        neuropil=n.get("neuropil"),
                        subsystem=n.get("subsystem"),
                        neurotransmitter=n.get("neurotransmitter"),
                        coords=n.get("coords"),
                        sex_dimorphic=n.get("sex_dimorphic", False),
                        in_degree=in_deg,
                        out_degree=out_deg,
                    )
                )

        edges_list: List[SubgraphEdge] = []
        total_synapses = 0
        for u in selected_nodes:
            for v in selected_nodes:
                if self.graph.has_edge(u, v):
                    edata = self.graph[u][v]
                    syn = edata["synapses"]
                    if syn >= request.min_synapses:
                        dist = edata.get("weight", max(0.1, 1000.0 / float(syn)))
                        edges_list.append(
                            SubgraphEdge(
                                source=u,
                                target=v,
                                synapses=syn,
                                biological_distance=round(dist, 2),
                                type=edata.get("type", "chemical"),
                                roi=edata.get("roi"),
                            )
                        )
                        total_synapses += syn

        latency = round((time.time() - start_time) * 1000, 2)
        prov = ComputationalProvenanceRecord(
            provenance_id=f"prov_subg_{uuid.uuid4().hex[:8]}",
            algorithm="subgraph_extraction",
            node_count=len(nodes_list),
            edge_count=len(edges_list),
            latency_ms=latency,
            parameters=request.model_dump(),
        )

        return SubgraphExtractionResponse(
            nodes=nodes_list,
            edges=edges_list,
            node_count=len(nodes_list),
            edge_count=len(edges_list),
            total_synapses=total_synapses,
            provenance=prov,
        )

    # Legacy extract_subgraph wrapper
    def extract_subgraph(self, node_ids: List[str], expand_hops: int = 0) -> Dict[str, Any]:
        """Backward-compatible extract_subgraph returning dict format."""
        req = SubgraphExtractionRequest(node_ids=node_ids, expand_hops=expand_hops, min_synapses=1)
        resp = self.extract_subgraph_v2(req)
        return {
            "nodes": [n.model_dump() for n in resp.nodes],
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "synapses": e.synapses,
                    "type": e.type
                }
                for e in resp.edges
            ]
        }

    # =========================================================================
    # Phase 3: Mathematical In-Silico Circuit Ablation
    # =========================================================================

    def simulate_ablation_v2(self, request: AblationRequestV2) -> AblationResponseV2:
        r"""
        In-Silico Neuronal Ablation Engine.
        Adheres strictly to docs/architecture.md Section 5:
        1. Perturbed Graph: G' = (V \ S, E')
        2. Reachable Target Loss: L_target = (|T_reach(G) \ T_reach(G')| / |T_reach(G)|) * 100%
        3. Path Severance Percentage: P_sev = ((K_paths(G) - K_paths(G')) / K_paths(G)) * 100%
        4. Throughput Loss: T_loss = ((W_flow(G) - W_flow(G')) / W_flow(G)) * 100%
           where W_flow = sum(min_{e in path} w_e) (bottleneck transmission capacity)
        5. Composite Vulnerability Score: V in [0.0, 10.0]
        """
        start_time = time.time()
        resolved_silenced = self.resolve_neuron_ids(request.silenced_ids)
        silenced_neurons = [self.neuron_lookup[sid] for sid in resolved_silenced if sid in self.neuron_lookup]

        # Default source/target sets if not explicitly provided (sensory -> motor)
        source_ids = request.source_ids or ["10001", "10005"]
        target_ids = request.target_ids or ["20145", "20146"]

        res_src = self.resolve_neuron_ids(source_ids)
        res_tgt = self.resolve_neuron_ids(target_ids)

        # 1. Baseline analysis (intact graph G)
        baseline_paths: List[List[str]] = []
        baseline_reachable_targets = set()
        baseline_throughput = 0

        for s in res_src:
            for t in res_tgt:
                if s != t and self.graph.has_node(s) and self.graph.has_node(t) and nx.has_path(self.graph, s, t):
                    baseline_reachable_targets.add(t)
                    paths = list(nx.all_simple_paths(self.graph, s, t, cutoff=request.max_depth))
                    baseline_paths.extend(paths)
                    for p in paths:
                        bottleneck = min(self.graph[p[i]][p[i+1]]["synapses"] for i in range(len(p)-1))
                        baseline_throughput += bottleneck

        baseline_path_count = len(baseline_paths)

        # 2. Perturbed graph G' = (V \ S, E')
        ablated_graph = self.graph.copy()
        ablated_graph.remove_nodes_from(resolved_silenced)

        # 3. Post-ablation analysis
        ablated_paths: List[List[str]] = []
        ablated_reachable_targets = set()
        ablated_throughput = 0
        alternative_detours = []

        for s in res_src:
            for t in res_tgt:
                if s != t and ablated_graph.has_node(s) and ablated_graph.has_node(t) and nx.has_path(ablated_graph, s, t):
                    ablated_reachable_targets.add(t)
                    paths = list(nx.all_simple_paths(ablated_graph, s, t, cutoff=request.max_depth))
                    ablated_paths.extend(paths)
                    for p in paths:
                        bottleneck = min(ablated_graph[p[i]][p[i+1]]["synapses"] for i in range(len(p)-1))
                        total_syn = sum(ablated_graph[p[i]][p[i+1]]["synapses"] for i in range(len(p)-1))
                        ablated_throughput += bottleneck
                        alternative_detours.append({
                            "path": [self.neuron_lookup[nid]["name"] for nid in p if nid in self.neuron_lookup],
                            "bottleneck_capacity": bottleneck,
                            "total_synapses": total_syn,
                            "hops": len(p) - 1,
                        })

        ablated_path_count = len(ablated_paths)

        # 4. Mathematical metrics calculation
        # Path Severance Percentage P_sev
        severance_pct = 0.0
        if baseline_path_count > 0:
            severance_pct = round(((baseline_path_count - ablated_path_count) / baseline_path_count) * 100.0, 1)

        # Throughput Loss Percentage T_loss
        throughput_loss_pct = 0.0
        if baseline_throughput > 0:
            throughput_loss_pct = round(((baseline_throughput - ablated_throughput) / baseline_throughput) * 100.0, 1)

        # Reachable Target Loss L_target
        base_reach_count = len(baseline_reachable_targets)
        ablate_reach_count = len(ablated_reachable_targets)
        target_loss_pct = 0.0
        if base_reach_count > 0:
            lost_targets = len(baseline_reachable_targets - ablated_reachable_targets)
            target_loss_pct = round((lost_targets / base_reach_count) * 100.0, 1)

        is_completely_severed = (ablated_path_count == 0 and baseline_path_count > 0)

        # Composite Vulnerability Score V: [0.0, 10.0]
        # V = min(10.0, round((0.5 * P_sev + 0.3 * T_loss + 0.2 * L_target) / 10.0, 2))
        raw_vuln = (0.5 * severance_pct + 0.3 * throughput_loss_pct + 0.2 * target_loss_pct) / 10.0
        vuln_score = min(10.0, max(0.0, round(raw_vuln, 2)))

        # Scientific interpretation text
        silenced_names = ", ".join([n["name"] for n in silenced_neurons])
        if is_completely_severed:
            explanation = (
                f"Catastrophic Circuit Failure: Ablating [{silenced_names}] severs 100% of synaptic pathways "
                f"between specified sensory inputs and motor outputs. Reachable Target Loss: {target_loss_pct}%. "
                f"No functional bypass circuit exists in the connectome."
            )
        elif severance_pct > 60:
            explanation = (
                f"Severe Circuit Impairment: Silencing [{silenced_names}] destroys {severance_pct}% of available "
                f"transmission routes and eliminates {throughput_loss_pct}% of synaptic bottleneck capacity. "
                f"{ablated_path_count} sub-optimal polysynaptic detour(s) remain with reduced transmission throughput."
            )
        else:
            explanation = (
                f"Partial Circuit Redundancy: Ablation of [{silenced_names}] causes {severance_pct}% pathway loss. "
                f"The connectome preserves robust collateral pathways through secondary descending neurons."
            )

        latency = round((time.time() - start_time) * 1000, 2)
        prov = ComputationalProvenanceRecord(
            provenance_id=f"prov_ablate_{uuid.uuid4().hex[:8]}",
            algorithm="insilico_ablation_perturbation",
            node_count=self.graph.number_of_nodes(),
            edge_count=self.graph.number_of_edges(),
            latency_ms=latency,
            parameters=request.model_dump(),
        )

        return AblationResponseV2(
            silenced_neurons=silenced_neurons,
            baseline_paths_count=baseline_path_count,
            ablated_paths_count=ablated_path_count,
            severance_percentage=severance_pct,
            baseline_throughput=baseline_throughput,
            ablated_throughput=ablated_throughput,
            throughput_loss_percentage=throughput_loss_pct,
            baseline_reachable_targets=base_reach_count,
            ablated_reachable_targets=ablate_reach_count,
            target_loss_percentage=target_loss_pct,
            is_completely_severed=is_completely_severed,
            vulnerability_score=vuln_score,
            alternative_detours=alternative_detours[:5],
            scientific_explanation=explanation,
            provenance=prov,
        )

    # Legacy simulate_ablation wrapper
    def simulate_ablation(
        self,
        silenced_ids: List[str],
        source_ids: Optional[List[str]] = None,
        target_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Backward-compatible simulate_ablation wrapper."""
        req = AblationRequestV2(
            silenced_ids=silenced_ids,
            source_ids=source_ids,
            target_ids=target_ids,
            max_depth=5
        )
        resp = self.simulate_ablation_v2(req)
        return {
            "silenced_neurons": resp.silenced_neurons,
            "baseline_paths_count": resp.baseline_paths_count,
            "ablated_paths_count": resp.ablated_paths_count,
            "severance_percentage": resp.severance_percentage,
            "throughput_loss_percentage": resp.throughput_loss_percentage,
            "target_loss_percentage": resp.target_loss_percentage,
            "is_completely_severed": resp.is_completely_severed,
            "vulnerability_score": resp.vulnerability_score,
            "alternative_detours": resp.alternative_detours,
            "explanation": resp.scientific_explanation
        }

    # =========================================================================
    # Phase 3: Topological Invariant Statistics
    # =========================================================================

    def get_topology_statistics(self) -> GraphTopologyResponse:
        """
        Compute global topological invariants of the connectome directed graph.
        """
        start_time = time.time()
        n = self.graph.number_of_nodes()
        m = self.graph.number_of_edges()
        total_synapses = sum(self.graph[u][v]["synapses"] for u, v in self.graph.edges())

        density = round(nx.density(self.graph), 5) if n > 1 else 0.0
        reciprocity = round(nx.reciprocity(self.graph), 4) if m > 0 else 0.0
        scc_count = nx.number_strongly_connected_components(self.graph) if n > 0 else 0
        wcc_count = nx.number_weakly_connected_components(self.graph) if n > 0 else 0
        is_dag = nx.is_directed_acyclic_graph(self.graph) if n > 0 else True
        avg_degree = round(sum(dict(self.graph.degree()).values()) / float(n), 2) if n > 0 else 0.0

        subsystems: Dict[str, int] = {}
        for n_id in self.graph.nodes():
            sub = self.neuron_lookup.get(n_id, {}).get("subsystem", "General")
            subsystems[sub] = subsystems.get(sub, 0) + 1

        latency = round((time.time() - start_time) * 1000, 2)
        prov = ComputationalProvenanceRecord(
            provenance_id=f"prov_topo_{uuid.uuid4().hex[:8]}",
            algorithm="topological_invariants",
            node_count=n,
            edge_count=m,
            latency_ms=latency,
            parameters={},
        )

        return GraphTopologyResponse(
            node_count=n,
            edge_count=m,
            total_synapses=total_synapses,
            is_directed=self.graph.is_directed(),
            density=density,
            reciprocity=reciprocity,
            strongly_connected_components=scc_count,
            weakly_connected_components=wcc_count,
            is_dag=is_dag,
            average_degree=avg_degree,
            subsystem_distribution=subsystems,
            provenance=prov,
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Legacy graph statistics for health check and backward compatibility."""
        subsystems = {}
        for n_id, n_info in self.neuron_lookup.items():
            sub = n_info.get("subsystem", "General")
            subsystems[sub] = subsystems.get(sub, 0) + 1

        total_synapses = sum(self.graph[u][v]["synapses"] for u, v in self.graph.edges())
        return {
            "total_neurons": self.graph.number_of_nodes(),
            "total_synapses": total_synapses,
            "total_connections": self.graph.number_of_edges(),
            "subsystem_counts": subsystems,
            "presets_available": len(SHOWCASE_PRESETS),
            "is_directed": self.graph.is_directed(),
        }


# Global singleton engine instance
graph_engine = ConnectomeGraphEngine()
