"""
Graph-RAG Agent for FlyConnectome AI.
Executes mathematically verified graph traversals on the connectome multigraph,
extracts 3D subgraphs, calculates synaptic flow metrics, and runs in-silico ablation.
"""

from typing import Dict, List, Any
from ..graph.engine import graph_engine


class GraphRAGAgent:
    def __init__(self):
        self.name = "Connectome Graph-RAG & Traversal Agent"

    def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute graph operations based on the planner's specifications.
        """
        sources = plan.get("source_neuron_ids", [])
        targets = plan.get("target_neuron_ids", [])
        ablation_targets = plan.get("ablation_target_ids", [])
        is_ablation = plan.get("is_ablation_requested", False)

        thought_steps = []
        thought_steps.append(f"Executing Graph-RAG traversal from {len(sources)} source candidate(s) to {len(targets)} target(s).")

        # 1. Traverse connectome graph
        circuit_res = graph_engine.find_circuit_pathways(
            source_ids=sources,
            target_ids=targets,
            max_depth=5,
            cutoff_paths=8
        )

        paths = circuit_res.get("paths", [])
        subgraph = circuit_res.get("subgraph", {"nodes": [], "edges": []})
        bottlenecks = circuit_res.get("bottlenecks", [])

        thought_steps.append(f"Discovered {len(paths)} synaptic pathway(s) spanning {len(subgraph['nodes'])} neurons and {len(subgraph['edges'])} synaptic connections.")

        if paths:
            strongest_path = paths[0]
            names_chain = " → ".join(strongest_path["node_names"])
            thought_steps.append(f"Identified primary high-throughput pathway: {names_chain} ({strongest_path['total_synapses']} cumulative synapses).")

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
            "sources": circuit_res.get("sources", []),
            "targets": circuit_res.get("targets", []),
            "total_pathways_found": circuit_res.get("total_pathways_found", 0),
            "thought_log": thought_steps
        }


graph_rag_agent = GraphRAGAgent()
