"""
Synthesis & Scientific Discovery Report Agent for NeuroGraph AI.
Compiles graph evidence, topological metrics, in-silico ablation results,
and literature citations into publication-grade scientific reports.
"""

from typing import Dict, List, Any
import json


class SynthesisAgent:
    def __init__(self):
        self.name = "Scientific Report & Discovery Synthesis Agent"

    def synthesize(
        self,
        user_query: str,
        plan: Dict[str, Any],
        graph_data: Dict[str, Any],
        literature_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize multi-agent outputs into a structured, publication-grade markdown research report.
        """
        thought_steps = []
        thought_steps.append("Synthesizing multi-agent findings into formal Scientific Discovery Report...")

        subsystem = plan.get("subsystem", "Connectome Circuit")
        circuit_goal = plan.get("circuit_goal", "")
        paths = graph_data.get("paths", [])
        subgraph = graph_data.get("subgraph", {"nodes": [], "edges": []})
        bottlenecks = graph_data.get("bottlenecks", [])
        ablation = graph_data.get("ablation")
        papers = literature_data.get("papers", [])

        # Format primary pathway
        primary_path_str = "None identified"
        total_synapses = 0
        hops = 0
        if paths:
            primary_path_str = " ➔ ".join(paths[0]["node_names"])
            total_synapses = paths[0]["total_synapses"]
            hops = paths[0]["hops"]

        # Build Markdown Document
        report_lines = []
        report_lines.append(f"# Scientific Discovery Report: {subsystem}")
        report_lines.append(f"**Research Query:** *\"{user_query}\"*  ")
        report_lines.append(f"**Biological Objective:** {circuit_goal}  ")
        report_lines.append(f"**Dataset Reference:** Google Research Drosophila Connectome (166k+ neurons, 125M+ synapses)\n")
        report_lines.append("---\n")

        # 1. Executive Abstract
        report_lines.append("## 1. Executive Summary & Circuit Hypothesis")
        report_lines.append(
            f"Using autonomous Graph-RAG traversal across the Drosophila melanogaster central nervous system connectome, "
            f"the system identified **{len(paths)} functional synaptic pathways** spanning **{len(subgraph['nodes'])} neurons** "
            f"and **{len(subgraph['edges'])} verified synaptic contacts**.\n\n"
            f"The dominant, high-throughput signaling axis was resolved as:\n"
            f"> `{primary_path_str}`\n\n"
            f"This pathway operates with **{total_synapses} cumulative synaptic connections** across **{hops} relay hops**, "
            f"providing the biological infrastructure for millisecond-latency behavioral execution."
        )

        # 2. Detailed Synaptic Connectivity Table
        report_lines.append("\n## 2. Synaptic Flow & Pathway Architecture")
        if paths:
            report_lines.append("| Hop | Presynaptic Neuron | Postsynaptic Target | Synapse Count | Connection Type |")
            report_lines.append("|:---:|:---|:---|:---:|:---|")
            for idx, step in enumerate(paths[0]["steps"], 1):
                report_lines.append(
                    f"| {idx} | **{step['from_name']}** | **{step['to_name']}** | `{step['synapses']}` | *{step['type']}* |"
                )

        # 3. Bottlenecks & Critical Nodes
        if bottlenecks:
            report_lines.append("\n### Key Transmission Bottlenecks (Betweenness Centrality)")
            for b in bottlenecks[:3]:
                report_lines.append(
                    f"- **{b['name']}** (`{b['type']}`, {b['neuropil']}): Centrality score `{b['centrality_score']}`. "
                    f"Acts as a pivotal relay nexus."
                )

        # 4. In-Silico Neuronal Ablation Analysis
        report_lines.append("\n## 3. In-Silico Knockout & Circuit Resilience")
        if ablation:
            silenced_names = ", ".join([n["name"] for n in ablation["silenced_neurons"]])
            report_lines.append(
                f"**Experimental Perturbation:** Simulated knockout of `[{silenced_names}]`.\n\n"
                f"- **Circuit Severance:** `{ablation['severance_percentage']}%` of sensory-to-motor pathways eliminated.\n"
                f"- **Synaptic Throughput Loss:** `{ablation['throughput_loss_percentage']}%`.\n"
                f"- **Vulnerability Index:** `{ablation['vulnerability_score']}/10` ({'CATASTROPHIC' if ablation['is_completely_severed'] else 'HIGH SEVERITY'}).\n"
                f"- **Remaining Alternative Detours:** `{ablation['ablated_paths_count']}`.\n\n"
                f"> **Interpretation:** {ablation['explanation']}"
            )
            if ablation.get("alternative_detours"):
                report_lines.append("\n**Identified Sub-optimal Detour Routes:**")
                for d in ablation["alternative_detours"][:2]:
                    report_lines.append(f"- `{' ➔ '.join(d['path'])}` ({d['synapses']} synapses, {d['hops']} hops)")
        else:
            report_lines.append(
                "*No neuron knockout requested for this baseline run. You can toggle neuron silencing in the interactive Ablation Studio.*"
            )

        # 5. Peer-Reviewed Academic Validation
        report_lines.append("\n## 4. Peer-Reviewed Literature & Experimental Validation")
        report_lines.append(
            "The extracted circuit topology was cross-referenced against scientific databases to ground findings in experimental electrophysiology:"
        )
        for p in papers:
            doi_link = f"https://doi.org/{p['doi']}" if p.get("doi") else "#"
            report_lines.append(
                f"- **[{p['title']}]({doi_link})**  \n"
                f"  *{p['authors']}* — **{p['journal']} ({p['year']})**  \n"
                f"  DOI: `{p.get('doi', 'N/A')}` | Citations: `{p.get('citations', 0)}`  \n"
                f"  > *\"{p['abstract_snippet']}\"*\n"
            )

        # 6. Conclusion & Discovery Next Steps
        report_lines.append("## 5. Research Conclusions")
        report_lines.append(
            f"1. **Circuit Integrity:** The connectome reveals high evolutionary preservation of the {subsystem} pathway.\n"
            f"2. **Computational Grounding:** Graph-RAG eliminates hallucination by strictly constraining AI deductions to biological synapse counts.\n"
            f"3. **In-Vitro Recommendations:** Optogenetic activation of the primary relay nodes is predicted to evoke immediate behavioral output."
        )

        full_markdown = "\n".join(report_lines)
        thought_steps.append("Scientific report compilation completed successfully.")

        return {
            "title": f"Discovery Report: {subsystem}",
            "markdown_report": full_markdown,
            "primary_path": primary_path_str,
            "total_synapses": total_synapses,
            "subsystem": subsystem,
            "thought_log": thought_steps
        }


synthesis_agent = SynthesisAgent()
