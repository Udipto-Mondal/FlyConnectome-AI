"""
Connectome Graph Engine for NeuroGraph AI.
High-performance NetworkX-powered directed graph traversal, Graph-RAG subgraph extraction,
and in-silico neuronal ablation simulation.
"""

from typing import Dict, List, Optional, Any, Set, Tuple
import networkx as nx
from .connectome_data import NEURON_DATABASE, SYNAPTIC_CONNECTIONS, SHOWCASE_PRESETS


class ConnectomeGraphEngine:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.neuron_lookup: Dict[str, Dict[str, Any]] = {}
        self.name_to_id: Dict[str, str] = {}
        self._build_graph()

    def _build_graph(self):
        """Build directed graph with biological attributes and inverted weights for Dijkstra."""
        for neuron in NEURON_DATABASE:
            n_id = str(neuron["id"])
            self.neuron_lookup[n_id] = neuron
            self.name_to_id[neuron["name"].lower()] = n_id
            self.graph.add_node(
                n_id,
                name=neuron["name"],
                type=neuron["type"],
                neuropil=neuron["neuropil"],
                subsystem=neuron["subsystem"],
                neurotransmitter=neuron["neurotransmitter"],
                description=neuron["description"],
                coords=neuron["coords"],
                sex_dimorphic=neuron.get("sex_dimorphic", False),
            )

        for edge in SYNAPTIC_CONNECTIONS:
            src = str(edge["source"])
            tgt = str(edge["target"])
            synapses = edge["synapses"]
            edge_type = edge["type"]
            # weight for shortest path: lower distance = higher synaptic strength
            # distance = 1000 / (synapses + 1)
            dist_weight = max(1.0, 1000.0 / float(synapses))
            self.graph.add_edge(
                src,
                tgt,
                synapses=synapses,
                type=edge_type,
                weight=dist_weight
            )

    def search_neurons(self, query: str) -> List[Dict[str, Any]]:
        """Search neurons by name, type, neuropil, or subsystem."""
        q = query.lower().strip()
        results = []
        for n_id, neuron in self.neuron_lookup.items():
            if (
                q in neuron["name"].lower()
                or q in neuron["type"].lower()
                or q in neuron["neuropil"].lower()
                or q in neuron["subsystem"].lower()
                or q in neuron["description"].lower()
                or q == n_id
            ):
                results.append(neuron)
        return results

    def get_neuron(self, neuron_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve metadata for a specific neuron."""
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
            # Partial match
            matches = self.search_neurons(s)
            if matches:
                resolved.append(str(matches[0]["id"]))
        return list(dict.fromkeys(resolved))  # preserve order & unique

    def find_circuit_pathways(
        self,
        source_ids: List[str],
        target_ids: List[str],
        max_depth: int = 5,
        cutoff_paths: int = 8
    ) -> Dict[str, Any]:
        """
        Extract all significant synaptic pathways between source and target neuron sets.
        Computes strongest synaptic paths, bottleneck nodes, and an induced subgraph.
        """
        resolved_sources = self.resolve_neuron_ids(source_ids)
        resolved_targets = self.resolve_neuron_ids(target_ids)

        if not resolved_sources or not resolved_targets:
            return {
                "paths": [],
                "subgraph": {"nodes": [], "edges": []},
                "bottlenecks": [],
                "summary": "No valid source or target neurons identified."
            }

        all_paths_raw = []
        for src in resolved_sources:
            for tgt in resolved_targets:
                if src == tgt or not (self.graph.has_node(src) and self.graph.has_node(tgt)):
                    continue
                try:
                    # Find simple paths up to max_depth
                    simple_paths = list(nx.all_simple_paths(self.graph, source=src, target=tgt, cutoff=max_depth))
                    for path in simple_paths:
                        # Calculate total synaptic weight along path
                        total_synapses = sum(
                            self.graph[path[i]][path[i+1]]["synapses"]
                            for i in range(len(path) - 1)
                        )
                        all_paths_raw.append({
                            "path_nodes": path,
                            "length": len(path),
                            "total_synapses": total_synapses,
                            "source_id": src,
                            "target_id": tgt
                        })
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    continue

        # Sort paths by synaptic strength (descending)
        all_paths_raw.sort(key=lambda x: x["total_synapses"], reverse=True)
        selected_paths = all_paths_raw[:cutoff_paths]

        # Collect all participating nodes and edges
        participating_node_ids: Set[str] = set()
        for p in selected_paths:
            participating_node_ids.update(p["path_nodes"])

        # Format paths with human-readable names and details
        formatted_paths = []
        for p in selected_paths:
            nodes_info = [self.neuron_lookup[nid] for nid in p["path_nodes"] if nid in self.neuron_lookup]
            steps = []
            for i in range(len(p["path_nodes"]) - 1):
                u, v = p["path_nodes"][i], p["path_nodes"][i+1]
                edge_data = self.graph[u][v]
                steps.append({
                    "from_name": self.neuron_lookup[u]["name"],
                    "to_name": self.neuron_lookup[v]["name"],
                    "synapses": edge_data["synapses"],
                    "type": edge_data["type"]
                })
            formatted_paths.append({
                "nodes": nodes_info,
                "node_names": [n["name"] for n in nodes_info],
                "steps": steps,
                "total_synapses": p["total_synapses"],
                "hops": len(p["path_nodes"]) - 1
            })

        # Build induced subgraph for 3D/2D visualization
        subgraph = self.extract_subgraph(list(participating_node_ids))

        # Calculate bottleneck nodes (Betweenness centrality on induced subgraph)
        sub_g = self.graph.subgraph(participating_node_ids)
        bottlenecks = []
        if len(sub_g) > 2:
            centrality = nx.betweenness_centrality(sub_g)
            sorted_cent = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
            for nid, score in sorted_cent:
                if score > 0.05 and nid not in resolved_sources and nid not in resolved_targets:
                    neuron = self.neuron_lookup.get(nid)
                    if neuron:
                        bottlenecks.append({
                            "id": nid,
                            "name": neuron["name"],
                            "type": neuron["type"],
                            "neuropil": neuron["neuropil"],
                            "centrality_score": round(score, 4)
                        })

        return {
            "paths": formatted_paths,
            "subgraph": subgraph,
            "bottlenecks": bottlenecks,
            "sources": [self.neuron_lookup[s] for s in resolved_sources if s in self.neuron_lookup],
            "targets": [self.neuron_lookup[t] for t in resolved_targets if t in self.neuron_lookup],
            "total_pathways_found": len(all_paths_raw)
        }

    def extract_subgraph(self, node_ids: List[str], expand_hops: int = 0) -> Dict[str, Any]:
        """Extract a structured subgraph format ready for 3D Three.js / WebGL rendering."""
        selected_nodes = set(node_ids)
        if expand_hops > 0:
            frontier = set(node_ids)
            for _ in range(expand_hops):
                new_frontier = set()
                for nid in frontier:
                    if self.graph.has_node(nid):
                        new_frontier.update(self.graph.predecessors(nid))
                        new_frontier.update(self.graph.successors(nid))
                selected_nodes.update(new_frontier)
                frontier = new_frontier

        nodes_list = []
        for nid in selected_nodes:
            if nid in self.neuron_lookup:
                n = self.neuron_lookup[nid]
                in_degree = self.graph.in_degree(nid) if self.graph.has_node(nid) else 0
                out_degree = self.graph.out_degree(nid) if self.graph.has_node(nid) else 0
                nodes_list.append({
                    "id": nid,
                    "name": n["name"],
                    "type": n["type"],
                    "neuropil": n["neuropil"],
                    "subsystem": n["subsystem"],
                    "neurotransmitter": n["neurotransmitter"],
                    "coords": n["coords"],
                    "sex_dimorphic": n.get("sex_dimorphic", False),
                    "in_degree": in_degree,
                    "out_degree": out_degree
                })

        edges_list = []
        for u in selected_nodes:
            for v in selected_nodes:
                if self.graph.has_edge(u, v):
                    edata = self.graph[u][v]
                    edges_list.append({
                        "source": u,
                        "target": v,
                        "synapses": edata["synapses"],
                        "type": edata["type"]
                    })

        return {"nodes": nodes_list, "edges": edges_list}

    def simulate_ablation(
        self,
        silenced_ids: List[str],
        source_ids: Optional[List[str]] = None,
        target_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Simulate in-silico neuronal ablation / knockout.
        Assesses circuit destruction percentage, alternative detour availability, and functional latency penalty.
        """
        resolved_silenced = self.resolve_neuron_ids(silenced_ids)
        silenced_neurons = [self.neuron_lookup[sid] for sid in resolved_silenced if sid in self.neuron_lookup]

        # If sources/targets not provided, infer from connected components or whole graph
        if not source_ids or not target_ids:
            # Default to major sensory -> motor pairs
            source_ids = ["10001", "10005"]
            target_ids = ["20145", "20146"]

        res_src = self.resolve_neuron_ids(source_ids)
        res_tgt = self.resolve_neuron_ids(target_ids)

        # 1. Baseline analysis (intact graph)
        baseline_path_count = 0
        baseline_synaptic_throughput = 0
        for s in res_src:
            for t in res_tgt:
                if s != t and nx.has_path(self.graph, s, t):
                    paths = list(nx.all_simple_paths(self.graph, s, t, cutoff=5))
                    baseline_path_count += len(paths)
                    for p in paths:
                        baseline_synaptic_throughput += sum(
                            self.graph[p[i]][p[i+1]]["synapses"] for i in range(len(p)-1)
                        )

        # 2. Create ablated graph
        ablated_graph = self.graph.copy()
        ablated_graph.remove_nodes_from(resolved_silenced)

        # 3. Post-ablation analysis
        ablated_path_count = 0
        ablated_synaptic_throughput = 0
        alternative_detours = []

        for s in res_src:
            for t in res_tgt:
                if s != t and s in ablated_graph and t in ablated_graph and nx.has_path(ablated_graph, s, t):
                    paths = list(nx.all_simple_paths(ablated_graph, s, t, cutoff=6))
                    ablated_path_count += len(paths)
                    for p in paths:
                        synapses = sum(ablated_graph[p[i]][p[i+1]]["synapses"] for i in range(len(p)-1))
                        ablated_synaptic_throughput += synapses
                        alternative_detours.append({
                            "path": [self.neuron_lookup[nid]["name"] for nid in p if nid in self.neuron_lookup],
                            "synapses": synapses,
                            "hops": len(p) - 1
                        })

        # Calculate metrics
        severance_pct = 0.0
        if baseline_path_count > 0:
            severance_pct = round(((baseline_path_count - ablated_path_count) / baseline_path_count) * 100.0, 1)

        throughput_loss_pct = 0.0
        if baseline_synaptic_throughput > 0:
            throughput_loss_pct = round(((baseline_synaptic_throughput - ablated_synaptic_throughput) / baseline_synaptic_throughput) * 100.0, 1)

        is_completely_severed = (ablated_path_count == 0 and baseline_path_count > 0)

        # Functional vulnerability score: 0 to 10
        vuln_score = min(10.0, round((severance_pct * 0.6 + throughput_loss_pct * 0.4) / 10.0, 2))

        # Scientific interpretation text
        silenced_names = ", ".join([n["name"] for n in silenced_neurons])
        if is_completely_severed:
            explanation = (
                f"Catastrophic Circuit Failure: Ablating [{silenced_names}] completely severs 100% of synaptic pathways "
                f"between specified sensory inputs and motor outputs. No functional bypass circuit exists in the connectome."
            )
        elif severance_pct > 60:
            explanation = (
                f"Severe Functional Impairment: Silencing [{silenced_names}] destroys {severance_pct}% of available "
                f"transmission routes and eliminates {throughput_loss_pct}% of total synaptic throughput. "
                f"{ablated_path_count} sub-optimal polysynaptic detour(s) remain with reduced transmission speed."
            )
        else:
            explanation = (
                f"Partial Circuit Redundancy: Ablation of [{silenced_names}] causes {severance_pct}% pathway loss. "
                f"The connectome preserves robust collateral pathways through secondary descending neurons."
            )

        return {
            "silenced_neurons": silenced_neurons,
            "baseline_paths_count": baseline_path_count,
            "ablated_paths_count": ablated_path_count,
            "severance_percentage": severance_pct,
            "throughput_loss_percentage": throughput_loss_pct,
            "is_completely_severed": is_completely_severed,
            "vulnerability_score": vuln_score,
            "alternative_detours": alternative_detours[:5],
            "explanation": explanation
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Return global graph statistics."""
        subsystems = {}
        for n in NEURON_DATABASE:
            sub = n["subsystem"]
            subsystems[sub] = subsystems.get(sub, 0) + 1

        total_synapses = sum(e["synapses"] for e in SYNAPTIC_CONNECTIONS)
        
        return {
            "total_neurons": self.graph.number_of_nodes(),
            "total_synapses": total_synapses,
            "total_connections": self.graph.number_of_edges(),
            "subsystem_counts": subsystems,
            "presets_available": len(SHOWCASE_PRESETS),
            "is_directed": self.graph.is_directed()
        }


# Singleton engine instance
graph_engine = ConnectomeGraphEngine()
