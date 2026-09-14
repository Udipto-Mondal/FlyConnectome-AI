"""
Connectome Context Formatter for FlyConnectome AI (Phase 4).
Serializes connectome multigraph structures, verified Tier A neuron metadata,
and scored circuit pathways into dense, anti-hallucination prompt context for downstream LLMs.
"""

from typing import List, Dict, Any, Optional
from .models import ScoredPathway, GraphRAGContext
from ..graph.models import SubgraphNode, SubgraphEdge


class ConnectomeContextFormatter:
    """
    Constructs structured, prompt-ready markdown contexts from connectome subgraphs.
    """

    @staticmethod
    def format_context(
        nodes: List[SubgraphNode],
        edges: List[SubgraphEdge],
        ranked_pathways: List[ScoredPathway],
        query: str,
        token_budget: int = 2500,
        compact_mode: bool = False
    ) -> GraphRAGContext:
        """
        Render a full GraphRAGContext with strict scientific guardrails and token budget management.
        """
        lines = []

        # 1. Anti-hallucination header & metadata
        lines.append("### CONNECTOME GRAPH-RAG GROUNDED CONTEXT (TIER A EVIDENCE)")
        lines.append("> **MANDATORY SCIENTIFIC CONSTRAINT**: The following neural circuit topology is retrieved directly from the verified Janelia / Google Research Drosophila Male CNS connectome (v1.0).")
        lines.append("> You MUST NOT invent, hallucinate, or extrapolate neuron body IDs, synaptic contacts, or neurotransmitter profiles not explicitly listed below.")
        lines.append(f"> **Query Grounding**: \"{query}\"")
        lines.append("")

        # 2. Ranked Pathways Section
        lines.append("#### Verified Neural Pathways (Ranked by Biological & Topological Relevance)")
        if not ranked_pathways:
            lines.append("*No continuous multi-synaptic pathways found matching the requested criteria.*")
        else:
            for i, p in enumerate(ranked_pathways[:6], 1):
                chain_str = " → ".join(p.node_names)
                id_chain = " → ".join(p.node_ids)
                lines.append(f"**Path {i}** [Relevance: {p.score.composite_score:.4f}]")
                lines.append(f"- **Circuit**: `{chain_str}`")
                lines.append(f"- **Janelia Body IDs**: `{id_chain}`")
                lines.append(f"- **Synaptic Contacts**: {p.total_synapses} cumulative contacts | Rate-limiting bottleneck: {p.bottleneck_synapses} synapses")
                lines.append(f"- **Biological Distance**: {p.biological_distance:.2f} (inverted resistance)")
                lines.append(f"- **Scientific Rationale**: {p.score.ranking_rationale}")
                lines.append("")

        # 3. Neuron Nodes Table
        lines.append("#### Verified Participating Neurons (Tier A Connectome Entities)")
        lines.append("| Body ID | Instance / Name | Cell Type | Soma / Neuropil | Neurotransmitter | Conf |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :---: |")
        for n in nodes:
            name = n.name or "Unnamed"
            ntype = n.type or "Unknown"
            soma = getattr(n, "neuropil", None) or getattr(n, "soma_neuropil", None) or "N/A"
            nt = n.neurotransmitter or "Unspecified"
            conf_val = getattr(n, "confidence", None)
            conf = f"{conf_val:.2f}" if conf_val is not None else "1.00"
            lines.append(f"| `{n.id}` | {name} | {ntype} | {soma} | {nt} | {conf} |")
        lines.append("")

        # 4. Direct Synaptic Adjacency
        lines.append("#### Verified Synaptic Connections")
        if not edges:
            lines.append("*No direct synaptic connections identified in the active subgraph.*")
        else:
            lines.append("| Presynaptic | Postsynaptic | Synapses | ROI | Transmission |")
            lines.append("| :--- | :--- | :---: | :--- | :--- |")
            # Sort edges by synapses/weight descending
            sorted_edges = sorted(edges, key=lambda e: getattr(e, "synapses", getattr(e, "weight", 0)), reverse=True)
            for e in sorted_edges[:30]:
                roi = e.roi or "Unassigned"
                syn_cnt = getattr(e, "synapses", getattr(e, "weight", 0))
                trans_type = getattr(e, "type", "chemical")
                lines.append(f"| `{e.source}` | `{e.target}` | **{syn_cnt}** | {roi} | {trans_type} |")
            if len(sorted_edges) > 30:
                lines.append(f"| ... | *({len(sorted_edges) - 30} additional synaptic contacts omitted for brevity)* | ... | ... | ... |")
        lines.append("")

        raw_text = "\n".join(lines)

        # Estimate tokens (~4 characters per token)
        char_limit = token_budget * 4
        if len(raw_text) > char_limit:
            raw_text = raw_text[:char_limit] + "\n\n*(Notice: Connectome context truncated to comply with token budget constraint)*"

        est_tokens = len(raw_text) // 4

        # Compile dense graph summary for machine reasoning
        total_syn_wt = sum(getattr(e, "synapses", getattr(e, "weight", 0)) for e in edges)
        dense_summary = {
            "query": query,
            "neuron_count": len(nodes),
            "synapse_count": len(edges),
            "top_path": ranked_pathways[0].model_dump() if ranked_pathways else None,
            "participating_ids": [n.id for n in nodes],
            "total_synaptic_weight": total_syn_wt,
        }

        # Tier A provenance records
        tier_a_prov = [
            {
                "body_id": n.id,
                "instance": n.name,
                "type": n.type,
                "dataset": "Drosophila Male CNS v1.0",
                "source": "Janelia / Google Research",
            }
            for n in nodes
        ]

        return GraphRAGContext(
            markdown_context=raw_text,
            dense_graph_summary=dense_summary,
            total_nodes=len(nodes),
            total_edges=len(edges),
            token_count_estimate=est_tokens,
            tier_a_provenance=tier_a_prov
        )


context_formatter = ConnectomeContextFormatter()
