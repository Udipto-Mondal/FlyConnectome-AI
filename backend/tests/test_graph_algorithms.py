"""
Automated Test Suite for NeuroGraph AI Graph Engine & Graph Algorithms (Phase 3).
Validates:
- Dijkstra biological distance pathfinding
- Directed simple path traversals
- Betweenness bottleneck centrality, Closeness, PageRank, and Degree
- In-silico circuit ablation conforming to docs/architecture.md Section 5
- Subgraph extraction and 3D coordinate packaging
- Global topological invariant statistics
- REST API routes mounted under /api/v1/graph/*
- Tier C Computational Inference provenance records
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.graph import (
    graph_engine,
    PathSearchRequest,
    CentralityRequest,
    SubgraphExtractionRequest,
    AblationRequestV2,
)

client = TestClient(app)


def test_dijkstra_biological_distance():
    """Verify Dijkstra pathfinding prioritizes high-synapse biological channels."""
    req = PathSearchRequest(
        source_ids=["10005"],  # LC4
        target_ids=["20145"],  # TTMn
        algorithm="dijkstra",
        weight_metric="biological_distance",
        min_synapses=5
    )
    result = graph_engine.find_pathways_v2(req)

    assert result.total_pathways_found > 0
    assert len(result.paths) > 0

    best_path = result.paths[0]
    assert "LC4" in best_path.node_names[0]
    assert "TTMn" in best_path.node_names[-1]
    assert "Giant Fiber (GF_L)" in best_path.node_names or "Giant Fiber (GF_R)" in best_path.node_names

    # Check biological distance calculations: higher synapses = lower distance
    assert best_path.cumulative_biological_distance > 0.0
    assert best_path.total_synapses > 50
    assert best_path.bottleneck_synapses >= 5
    assert best_path.hops == len(best_path.steps)

    # Check Tier C provenance record
    assert result.provenance.tier == "Tier C: Computational Inference"
    assert "dijkstra" in result.provenance.algorithm
    assert result.provenance.node_count > 0


def test_all_simple_paths_with_depth_cutoff():
    """Verify all simple paths traversal with synaptic filtering and depth limit."""
    req = PathSearchRequest(
        source_ids=["10001"],  # Photoreceptor R1-R6
        target_ids=["20145"],  # TTMn
        algorithm="all_simple",
        max_depth=5,
        cutoff_paths=10,
        min_synapses=10,
        weight_metric="synapses"
    )
    result = graph_engine.find_pathways_v2(req)
    assert result.total_pathways_found >= 1
    # Check sorting: highest total synapses first
    if len(result.paths) > 1:
        assert result.paths[0].total_synapses >= result.paths[1].total_synapses


def test_betweenness_centrality_bottleneck_detection():
    """Verify Betweenness Centrality identifies Giant Fiber as primary bottleneck hub."""
    req = CentralityRequest(
        node_ids=None,  # entire graph
        metrics=["betweenness", "closeness", "pagerank", "degree"]
    )
    result = graph_engine.compute_centrality_v2(req)

    assert len(result.nodes) > 20
    assert len(result.top_bottlenecks) > 0

    # Giant Fiber (10234) should be among the top bottlenecks
    gf_nodes = [b for b in result.top_bottlenecks if b.node_id in ["10234", "10235"]]
    assert len(gf_nodes) > 0
    assert gf_nodes[0].betweenness_centrality > 0.01

    # Check node centrality attributes
    sample = result.nodes[0]
    assert sample.in_degree >= 0
    assert sample.out_degree >= 0
    assert sample.in_synapses >= 0
    assert sample.out_synapses >= 0
    assert result.provenance.tier == "Tier C: Computational Inference"


def test_insilico_ablation_section_5_mathematics():
    """
    Verify In-Silico Ablation adheres to docs/architecture.md Section 5 equations:
    - Path Severance (P_sev)
    - Throughput Loss (T_loss)
    - Reachable Target Loss (L_target)
    - Composite Vulnerability Score (V in [0.0, 10.0])
    """
    req = AblationRequestV2(
        silenced_ids=["10234"],  # Silencing GF_L
        source_ids=["10005"],    # LC4
        target_ids=["20145"],    # TTMn
        max_depth=6
    )
    result = graph_engine.simulate_ablation_v2(req)

    assert len(result.silenced_neurons) == 1
    assert result.silenced_neurons[0]["name"] == "Giant Fiber (GF_L)"

    # Severance percentage should be strictly positive
    assert result.severance_percentage > 0.0
    assert result.throughput_loss_percentage > 0.0
    assert 0.0 <= result.vulnerability_score <= 10.0
    assert result.baseline_throughput > 0

    # Scientific explanation should contain formal metrics
    assert "Ablat" in result.scientific_explanation or "Silencing" in result.scientific_explanation
    assert result.provenance.tier == "Tier C: Computational Inference"
    assert result.provenance.algorithm == "insilico_ablation_perturbation"


def test_subgraph_extraction_with_3d_coordinates():
    """Verify subgraph extraction packages 3D spatial coordinates and degrees."""
    req = SubgraphExtractionRequest(
        node_ids=["10005", "10234", "20145"],
        expand_hops=1,
        min_synapses=5
    )
    result = graph_engine.extract_subgraph_v2(req)

    assert result.node_count >= 3
    assert result.edge_count >= 2
    assert result.total_synapses > 0

    # Verify 3D centroid coordinates format [x, y, z]
    for node in result.nodes:
        assert isinstance(node.coords, list)
        assert len(node.coords) == 3
        assert node.in_degree >= 0
        assert node.out_degree >= 0

    for edge in result.edges:
        assert edge.synapses >= 5
        assert edge.biological_distance > 0.0


def test_graph_topology_statistics():
    """Verify global topological invariants calculation."""
    topo = graph_engine.get_topology_statistics()

    assert topo.node_count > 20
    assert topo.edge_count > 30
    assert topo.total_synapses > 5000
    assert topo.is_directed is True
    assert 0.0 < topo.density < 1.0
    assert 0.0 <= topo.reciprocity <= 1.0
    assert topo.strongly_connected_components >= 1
    assert topo.weakly_connected_components >= 1
    assert len(topo.subsystem_distribution) > 0
    assert topo.provenance.tier == "Tier C: Computational Inference"


# =============================================================================
# REST API Endpoint Tests (/api/v1/graph/*)
# =============================================================================

def test_api_graph_paths_endpoint():
    """Test POST /api/v1/graph/paths."""
    payload = {
        "source_ids": ["10005"],
        "target_ids": ["20145"],
        "algorithm": "dijkstra",
        "max_depth": 5,
        "cutoff_paths": 5,
        "min_synapses": 1,
        "weight_metric": "biological_distance"
    }
    response = client.post("/api/v1/graph/paths", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "paths" in data
    assert len(data["paths"]) > 0
    assert "provenance" in data
    assert data["provenance"]["tier"] == "Tier C: Computational Inference"


def test_api_graph_centrality_endpoint():
    """Test POST /api/v1/graph/centrality."""
    payload = {
        "node_ids": ["10005", "10006", "10234", "20145", "20146"],
        "metrics": ["betweenness", "closeness", "pagerank", "degree"]
    }
    response = client.post("/api/v1/graph/centrality", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert len(data["nodes"]) == 5
    assert "top_bottlenecks" in data
    assert "provenance" in data


def test_api_graph_subgraph_endpoint():
    """Test POST /api/v1/graph/subgraph."""
    payload = {
        "node_ids": ["10005", "10234"],
        "expand_hops": 1,
        "min_synapses": 1
    }
    response = client.post("/api/v1/graph/subgraph", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert data["node_count"] >= 2
    assert "provenance" in data


def test_api_graph_ablation_endpoint():
    """Test POST /api/v1/graph/ablation."""
    payload = {
        "silenced_ids": ["10234"],
        "source_ids": ["10005"],
        "target_ids": ["20145"],
        "max_depth": 5
    }
    response = client.post("/api/v1/graph/ablation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["severance_percentage"] > 0
    assert data["vulnerability_score"] > 0
    assert "scientific_explanation" in data
    assert data["provenance"]["tier"] == "Tier C: Computational Inference"


def test_api_graph_topology_endpoint():
    """Test GET /api/v1/graph/topology."""
    response = client.get("/api/v1/graph/topology")
    assert response.status_code == 200
    data = response.json()
    assert data["node_count"] > 0
    assert data["edge_count"] > 0
    assert data["density"] > 0
    assert "provenance" in data


def test_api_graph_statistics_endpoint():
    """Test GET /api/v1/graph/statistics."""
    response = client.get("/api/v1/graph/statistics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_neurons"] > 0
    assert data["total_synapses"] > 0
