"""
Automated Test Suite for FlyConnectome AI Graph-RAG Retrieval System (Phase 4).
Tests:
- Multi-factor relevance scoring formulation and mathematical bounds
- Anti-hallucination connectome context formatting and token budgeting
- Natural language biological entity grounding
- End-to-end Graph-RAG retrieval pipeline
- REST API routes (/api/v1/graph-rag/*)
- Agent integration with GraphRAGAgent and Orchestrator
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.graph_rag import (
    circuit_scorer,
    context_formatter,
    graph_rag_retriever,
    GraphRAGQueryRequest,
    ScoredPathway,
)
from app.graph.engine import graph_engine
from app.graph.models import SubgraphNode, SubgraphEdge
from app.agents.graph_rag_agent import graph_rag_agent

client = TestClient(app)


def test_scorer_bounds_and_components():
    """Verify that multi-factor relevance scores are mathematically bounded in [0.0, 1.0]."""
    node_ids = ["10005", "10234", "10500"]
    node_names = ["LC4_L", "GF_L", "MN_TDT_L"]

    # High capacity pathway
    score_high = circuit_scorer.score_pathway(
        node_ids=node_ids,
        node_names=node_names,
        total_synapses=150,
        biological_distance=20.0,
        bottleneck_synapses=45,
        query="visual escape circuit LC4 to Giant Fiber",
    )

    assert 0.0 <= score_high.synaptic_weight_score <= 1.0
    assert 0.0 <= score_high.biological_distance_score <= 1.0
    assert 0.0 <= score_high.centrality_hub_score <= 1.0
    assert 0.0 <= score_high.query_alignment_score <= 1.0
    assert 0.0 <= score_high.composite_score <= 1.0
    assert score_high.composite_score > 0.5
    assert "relevance:" in score_high.ranking_rationale.lower()

    # Weak/fragile pathway
    score_weak = circuit_scorer.score_pathway(
        node_ids=node_ids,
        node_names=node_names,
        total_synapses=2,
        biological_distance=1000.0,
        bottleneck_synapses=1,
        query="unrelated olfactory query",
    )

    assert 0.0 <= score_weak.composite_score <= 1.0
    # Strong circuit must rank higher than weak circuit
    assert score_high.composite_score > score_weak.composite_score


def test_scorer_query_and_roi_alignment():
    """Verify ROI and neurotransmitter matching increases query alignment score."""
    node_ids = ["10234", "10235"]
    node_names = ["GF_L", "GF_R"]

    score_aligned = circuit_scorer.score_pathway(
        node_ids=node_ids,
        node_names=node_names,
        total_synapses=60,
        biological_distance=30.0,
        bottleneck_synapses=30,
        node_metadata=graph_engine.neuron_lookup,
        query="Giant Fiber cholinergic GNG neurons",
        target_rois=["GNG"],
        target_neurotransmitters=["acetylcholine"],
    )

    score_unaligned = circuit_scorer.score_pathway(
        node_ids=node_ids,
        node_names=node_names,
        total_synapses=60,
        biological_distance=30.0,
        bottleneck_synapses=30,
        node_metadata=graph_engine.neuron_lookup,
        query="GABAergic Antennal Lobe circuits",
        target_rois=["AL"],
        target_neurotransmitters=["gaba"],
    )

    assert score_aligned.query_alignment_score >= score_unaligned.query_alignment_score


def test_context_formatter_tier_a_anti_hallucination():
    """Verify context formatting includes Tier A constraints, node tables, and edge listings."""
    nodes = [
        SubgraphNode(id="10234", name="GF_L", type="Giant Fiber", neuropil="GNG", neurotransmitter="acetylcholine"),
        SubgraphNode(id="10005", name="LC4_L", type="Visual Projection", neuropil="ME_L", neurotransmitter="acetylcholine"),
    ]
    edges = [
        SubgraphEdge(source="10005", target="10234", synapses=78, biological_distance=12.8, roi="GNG", type="chemical"),
    ]

    path_score = circuit_scorer.score_pathway(
        node_ids=["10005", "10234"],
        node_names=["LC4_L", "GF_L"],
        total_synapses=78,
        biological_distance=12.8,
        bottleneck_synapses=78,
        query="LC4 to Giant Fiber",
    )

    ranked_path = ScoredPathway(
        path_id="test_path_1",
        node_ids=["10005", "10234"],
        node_names=["LC4_L", "GF_L"],
        total_synapses=78,
        biological_distance=12.8,
        bottleneck_synapses=78,
        bottleneck_edge=["10005", "10234"],
        score=path_score,
    )

    context = context_formatter.format_context(
        nodes=nodes,
        edges=edges,
        ranked_pathways=[ranked_path],
        query="escape jump circuit",
        token_budget=2000,
    )

    md = context.markdown_context
    assert "TIER A EVIDENCE" in md
    assert "MANDATORY SCIENTIFIC CONSTRAINT" in md
    assert "10234" in md
    assert "10005" in md
    assert "GF_L" in md
    assert "LC4_L" in md
    assert "78" in md
    assert context.total_nodes == 2
    assert context.total_edges == 1
    assert context.token_count_estimate > 0
    assert len(context.tier_a_provenance) == 2


def test_context_formatter_token_budget_truncation():
    """Verify that specifying a tight token budget truncates cleanly without error."""
    nodes = [
        SubgraphNode(id=f"1000{i}", name=f"Neuron_{i}", type="TypeA", neuropil="GNG", neurotransmitter="acetylcholine")
        for i in range(25)
    ]
    edges = [
        SubgraphEdge(source=f"1000{i}", target=f"1000{i+1}", synapses=10, biological_distance=100.0, roi="GNG", type="chemical")
        for i in range(24)
    ]

    context = context_formatter.format_context(
        nodes=nodes,
        edges=edges,
        ranked_pathways=[],
        query="large circuit test",
        token_budget=200,  # very small budget (800 chars)
    )

    assert len(context.markdown_context) <= 1000
    assert "truncated" in context.markdown_context.lower()


def test_entity_grounding_known_circuit():
    """Verify entity grounding extracts canonical LC4 and Giant Fiber body IDs from escape query."""
    grounded = graph_rag_retriever.ground_entities(query="Giant Fiber visual escape pathway via LC4")
    assert len(grounded["sources"]) >= 1
    assert len(grounded["targets"]) >= 1
    all_grounded = grounded["sources"] + grounded["targets"] + grounded["seeds"]
    assert any("10234" in gid or "gf" in gid.lower() for gid in all_grounded)
    assert any("10005" in gid or "lc4" in gid.lower() for gid in all_grounded)


def test_retriever_end_to_end():
    """Verify end-to-end retrieval produces scored pathways, nodes, edges, and RAG context."""
    req = GraphRAGQueryRequest(
        query="Trace visual escape circuit from LC4 to Giant Fiber",
        min_synapses=5,
        max_depth=4,
        max_pathways=3,
        token_budget=2500,
    )

    res = graph_rag_retriever.retrieve(req)
    assert res.query == req.query
    assert len(res.nodes) > 0
    assert len(res.edges) > 0
    assert len(res.ranked_pathways) > 0

    top_p = res.ranked_pathways[0]
    assert top_p.score.composite_score > 0.0
    assert len(top_p.node_ids) >= 2
    assert res.context.total_nodes == len(res.nodes)
    assert "TIER A" in res.context.markdown_context
    assert res.provenance.algorithm == "graph_rag_retrieval_v1"
    assert res.provenance.latency_ms >= 0.0


def test_retriever_unilateral_seed_expansion():
    """Verify retrieval functions when only seed neuron IDs are supplied."""
    req = GraphRAGQueryRequest(
        query="Analyze local connectivity around Giant Fiber",
        seed_neuron_ids=["10234"],
        min_synapses=1,
        max_depth=2,
    )
    res = graph_rag_retriever.retrieve(req)
    assert len(res.nodes) >= 1
    node_ids = [n.id for n in res.nodes]
    assert "10234" in node_ids


def test_api_graph_rag_status_endpoint():
    """Verify GET /api/v1/graph-rag/status returns operational diagnostics."""
    response = client.get("/api/v1/graph-rag/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert data["phase"] == "Phase 4"
    assert "capabilities" in data
    assert len(data["capabilities"]) >= 4


def test_api_graph_rag_retrieve_endpoint():
    """Verify POST /api/v1/graph-rag/retrieve returns complete retrieval payload."""
    payload = {
        "query": "escape circuit LC4 to Giant Fiber",
        "min_synapses": 5,
        "max_pathways": 3,
        "token_budget": 2000
    }
    response = client.post("/api/v1/graph-rag/retrieve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert "ranked_pathways" in data
    assert "context" in data
    assert "provenance" in data
    assert len(data["ranked_pathways"]) > 0


def test_api_graph_rag_retrieve_empty_query_error():
    """Verify POST /api/v1/graph-rag/retrieve with whitespace query returns 400 error."""
    response = client.post("/api/v1/graph-rag/retrieve", json={"query": "   "})
    assert response.status_code == 400


def test_api_graph_rag_score_path_endpoint():
    """Verify POST /api/v1/graph-rag/score-path computes relevance score for explicit path."""
    payload = {
        "node_ids": ["10005", "10234"],
        "query": "visual escape",
        "target_rois": ["GNG"]
    }
    response = client.post("/api/v1/graph-rag/score-path", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "composite_score" in data
    assert 0.0 <= data["composite_score"] <= 1.0
    assert "ranking_rationale" in data


def test_api_graph_rag_format_context_endpoint():
    """Verify POST /api/v1/graph-rag/format-context compiles direct prompt context."""
    payload = {
        "node_ids": ["10234", "10235"],
        "query": "Giant Fiber Bilateral Pair",
        "token_budget": 1500
    }
    response = client.post("/api/v1/graph-rag/format-context", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "markdown_context" in data
    assert "TIER A" in data["markdown_context"]
    assert data["total_nodes"] == 2


def test_graph_rag_agent_orchestration():
    """Verify upgraded GraphRAGAgent returns scored pathways and compiled RAG context."""
    plan = {
        "query": "Visual escape reflex circuit",
        "source_neuron_ids": ["10005"],
        "target_neuron_ids": ["10234"],
        "is_ablation_requested": False
    }
    res = graph_rag_agent.execute(plan)
    assert "paths" in res
    assert "subgraph" in res
    assert "rag_context" in res
    assert "rag_summary" in res
    assert "tier_a_provenance" in res
    assert "TIER A EVIDENCE" in res["rag_context"]
    assert len(res["paths"]) > 0
    assert "relevance_score" in res["paths"][0]
