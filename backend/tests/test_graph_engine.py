"""
Automated Unit Tests for FlyConnectome AI Graph Engine.
"""

import pytest
from app.graph.engine import graph_engine


def test_graph_initialization():
    stats = graph_engine.get_statistics()
    assert stats["total_neurons"] > 20
    assert stats["total_synapses"] > 5000
    assert stats["is_directed"] is True


def test_visual_escape_pathway():
    # Source: LC4 (10005), Target: TTMn (20145)
    result = graph_engine.find_circuit_pathways(["10005"], ["20145"])
    assert len(result["paths"]) > 0
    primary_path = result["paths"][0]["node_names"]
    assert "LC4" in primary_path[0]
    assert "TTMn" in primary_path[-1]
    assert "Giant Fiber (GF_L)" in primary_path or "Giant Fiber (GF_R)" in primary_path


def test_insilico_ablation():
    # Silencing Giant Fiber should sever primary jump pathway
    ablation = graph_engine.simulate_ablation(
        silenced_ids=["10234"],
        source_ids=["10005"],
        target_ids=["20145"]
    )
    assert ablation["severance_percentage"] > 0
    assert ablation["vulnerability_score"] > 0
    assert len(ablation["silenced_neurons"]) == 1
    assert ablation["silenced_neurons"][0]["name"] == "Giant Fiber (GF_L)"


def test_subgraph_extraction():
    subgraph = graph_engine.extract_subgraph(["10005", "10234", "20145"])
    assert len(subgraph["nodes"]) == 3
    assert len(subgraph["edges"]) >= 2
    # Verify 3D coordinates present
    for node in subgraph["nodes"]:
        assert len(node["coords"]) == 3
