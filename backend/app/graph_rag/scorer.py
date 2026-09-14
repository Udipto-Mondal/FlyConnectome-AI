"""
Multi-Factor Circuit Relevance Scorer for FlyConnectome AI (Phase 4).
Mathematically scores candidate connectome circuit pathways across synaptic contact capacity,
biological resistance efficiency, interneuron hub centrality, and query intent alignment.
"""

from typing import List, Dict, Any, Optional
import networkx as nx
from .models import RelevanceScoreBreakdown


class CircuitRelevanceScorer:
    """
    Computes rigorous, normalized relevance scores for neural circuit pathways.
    """

    def __init__(
        self,
        weight_synapse: float = 0.35,
        weight_efficiency: float = 0.25,
        weight_centrality: float = 0.20,
        weight_query: float = 0.20
    ):
        self.w_syn = weight_synapse
        self.w_eff = weight_efficiency
        self.w_cent = weight_centrality
        self.w_qry = weight_query
        # Ensure normalization
        total_w = self.w_syn + self.w_eff + self.w_cent + self.w_qry
        if total_w > 0:
            self.w_syn /= total_w
            self.w_eff /= total_w
            self.w_cent /= total_w
            self.w_qry /= total_w

    def score_pathway(
        self,
        node_ids: List[str],
        node_names: List[str],
        total_synapses: int,
        biological_distance: float,
        bottleneck_synapses: int,
        graph: Optional[nx.DiGraph] = None,
        node_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
        query: str = "",
        target_rois: Optional[List[str]] = None,
        target_neurotransmitters: Optional[List[str]] = None,
        betweenness_cache: Optional[Dict[str, float]] = None
    ) -> RelevanceScoreBreakdown:
        """
        Evaluate a specific pathway and return a fully explained RelevanceScoreBreakdown.
        """
        hop_count = max(1, len(node_ids) - 1)
        node_meta = node_metadata or {}

        # 1. Synaptic Weight Score (Contact Abundance & Bottleneck Capacity)
        # Bottleneck saturation scale: 50 synapses is considered robust in Drosophila CNS
        bottleneck_term = min(1.0, bottleneck_synapses / 50.0)
        # Average synapses per edge: 30 synapses/edge is strong
        avg_synapses = total_synapses / float(hop_count)
        avg_term = min(1.0, avg_synapses / 60.0)
        s_syn = round(0.6 * bottleneck_term + 0.4 * avg_term, 4)
        s_syn = max(0.0, min(1.0, s_syn))

        # 2. Biological Distance Efficiency
        # Expected base distance: ~100.0 per hop for a solid 10-synapse edge
        norm_factor = max(1.0, 150.0 * hop_count)
        s_eff = round(1.0 / (1.0 + (biological_distance / norm_factor)), 4)
        s_eff = max(0.0, min(1.0, s_eff))

        # 3. Network Hub Centrality (Intermediate Nodes)
        intermediate_nodes = node_ids[1:-1]
        if not intermediate_nodes:
            # Direct monosynaptic connection has maximum structural efficiency
            s_cent = 1.0
        else:
            centrality_vals = []
            for nid in intermediate_nodes:
                if betweenness_cache and nid in betweenness_cache:
                    val = betweenness_cache[nid]
                elif graph and graph.has_node(nid):
                    # Local degree centrality fallback if betweenness cache not computed
                    deg = graph.degree(nid)
                    val = min(1.0, deg / 50.0)
                else:
                    val = 0.3
                centrality_vals.append(val)
            s_cent = round(sum(centrality_vals) / len(centrality_vals), 4)
            # Normalize to reasonable range [0.1, 1.0]
            s_cent = max(0.05, min(1.0, s_cent * 2.5))

        # 4. Query Alignment Score
        s_qry = 0.5  # Baseline neutral
        query_lower = query.lower()
        matched_aspects = 0
        total_aspects = 0

        # Check ROI overlap
        if target_rois:
            total_aspects += len(target_rois)
            for roi in target_rois:
                r_lower = roi.lower()
                for nid in node_ids:
                    meta = node_meta.get(nid, {})
                    rois_innervated = [str(r).lower() for r in meta.get("soma_neuropil", "").split(",")]
                    if any(r_lower in r for r in rois_innervated):
                        matched_aspects += 1
                        break

        # Check neurotransmitter overlap
        if target_neurotransmitters:
            total_aspects += len(target_neurotransmitters)
            for nt in target_neurotransmitters:
                nt_lower = nt.lower()
                for nid in node_ids:
                    meta = node_meta.get(nid, {})
                    actual_nt = str(meta.get("neurotransmitter", "")).lower()
                    if nt_lower in actual_nt:
                        matched_aspects += 1
                        break

        # Check lexical match in node names vs query
        if query_lower:
            total_aspects += 1
            path_text = " ".join([str(nid).lower() + " " + str(name).lower() for nid, name in zip(node_ids, node_names)])
            query_tokens = [w for w in query_lower.split() if len(w) >= 3]
            token_matches = sum(1 for tok in query_tokens if tok in path_text)
            if query_tokens and (token_matches / len(query_tokens)) > 0.2:
                matched_aspects += 1
            elif not query_tokens:
                matched_aspects += 1

        if total_aspects > 0:
            s_qry = round(max(0.1, min(1.0, matched_aspects / float(total_aspects))), 4)
        else:
            s_qry = 0.8  # No restrictive filters specified, defaults to high match

        # Composite Score
        composite = round(
            self.w_syn * s_syn +
            self.w_eff * s_eff +
            self.w_cent * s_cent +
            self.w_qry * s_qry,
            4
        )
        composite = max(0.0, min(1.0, composite))

        # Scientific Rationale Generator
        rationale_parts = []
        if s_syn >= 0.7:
            rationale_parts.append(f"High synaptic capacity ({total_synapses} total, bottleneck: {bottleneck_synapses})")
        elif s_syn >= 0.4:
            rationale_parts.append(f"Moderate synaptic capacity (bottleneck: {bottleneck_synapses})")
        else:
            rationale_parts.append(f"Low synaptic capacity (bottleneck: {bottleneck_synapses} contacts)")

        if s_eff >= 0.7:
            rationale_parts.append(f"high biological conductance (dist: {biological_distance:.1f})")
        else:
            rationale_parts.append(f"higher polysynaptic resistance (dist: {biological_distance:.1f})")

        if s_qry >= 0.7:
            rationale_parts.append("strong query & neuropil alignment")

        rationale = "; ".join(rationale_parts) + f". Composite relevance: {composite:.4f}."

        return RelevanceScoreBreakdown(
            synaptic_weight_score=s_syn,
            biological_distance_score=s_eff,
            centrality_hub_score=s_cent,
            query_alignment_score=s_qry,
            composite_score=composite,
            ranking_rationale=rationale
        )


circuit_scorer = CircuitRelevanceScorer()
