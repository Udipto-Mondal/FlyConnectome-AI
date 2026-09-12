"""
Phase 2 Automated Tests for Connectome Query Layer.
Tests neuron lookups, upstream/downstream partners, synaptic connectivity between neuron sets,
and REST API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.connectome.query_layer import ConnectomeQueryLayer
from app.connectome.models import NeuronModel, SynapticConnectionModel

client = TestClient(app)
ql = ConnectomeQueryLayer()


def test_get_neuron_by_body_id():
    """Verify neuron lookup by valid Janelia body ID returns correct NeuronModel."""
    res = ql.get_neuron(10234)
    assert res is not None
    assert "neuron" in res
    neuron = res["neuron"]
    assert neuron["body_id"] == 10234
    assert neuron["instance"] == "GF_L"
    assert neuron["type"] == "Giant Fiber"
    assert neuron["neurotransmitter"] == "acetylcholine"
    assert "provenance" in res
    assert res["provenance"]["dataset_name"] == "cns"


def test_get_nonexistent_neuron():
    """Verify lookup for non-existent body ID returns None."""
    res = ql.get_neuron(99999999)
    assert res is None


def test_find_neurons_by_type_and_instance():
    """Verify searching neurons by type or instance returns matches."""
    res = ql.find_neurons(query="Giant Fiber")
    assert res["count"] >= 2
    body_ids = [n["body_id"] for n in res["neurons"]]
    assert 10234 in body_ids
    assert 10235 in body_ids

    res_lc4 = ql.find_neurons(query="LC4")
    assert res_lc4["count"] >= 1
    assert res_lc4["neurons"][0]["body_id"] == 10005


def test_find_neurons_by_roi():
    """Verify filtering neurons by innervated ROI."""
    res = ql.find_neurons(roi="GNG")
    assert res["count"] >= 2
    for n in res["neurons"]:
        assert "GNG" in n["soma_neuropil"]


def test_get_upstream_partners():
    """Verify retrieving presynaptic partners of Giant Fiber (GF_L: 10234)."""
    res = ql.get_upstream_partners(body_id=10234, min_synapses=10)
    assert res["count"] >= 2
    pre_ids = [c["pre_body_id"] for c in res["connections"]]
    assert 10005 in pre_ids  # LC4
    assert 10006 in pre_ids  # LPLC2
    for c in res["connections"]:
        assert c["weight"] >= 10
        assert c["post_body_id"] == 10234


def test_get_downstream_partners():
    """Verify retrieving postsynaptic output partners of Giant Fiber (GF_L: 10234)."""
    res = ql.get_downstream_partners(body_id=10234, min_synapses=10)
    assert res["count"] >= 2
    post_ids = [c["post_body_id"] for c in res["connections"]]
    assert 10301 in post_ids  # PSI
    assert 20145 in post_ids  # TTMn
    for c in res["connections"]:
        assert c["pre_body_id"] == 10234
        assert c["weight"] >= 10


def test_get_connectivity_between_sets():
    """Verify querying direct connections between looming visual inputs and escape targets."""
    sources = [10005, 10006]
    targets = [10234, 10235]
    res = ql.get_connectivity(source_ids=sources, target_ids=targets, min_synapses=10)
    assert res["count"] >= 2
    for conn in res["connections"]:
        assert conn["pre_body_id"] in sources
        assert conn["post_body_id"] in targets
        assert conn["weight"] >= 10


def test_api_search_neurons_endpoint():
    """Test GET /api/v1/connectome/neurons endpoint."""
    response = client.get("/api/v1/connectome/neurons?query=Giant")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 2
    assert "provenance" in data


def test_api_get_neuron_endpoint():
    """Test GET /api/v1/connectome/neurons/{body_id} endpoint."""
    response = client.get("/api/v1/connectome/neurons/10234")
    assert response.status_code == 200
    data = response.json()
    assert data["neuron"]["body_id"] == 10234
    assert data["neuron"]["type"] == "Giant Fiber"


def test_api_get_neuron_not_found():
    """Test GET /api/v1/connectome/neurons/{body_id} 404 for invalid ID."""
    response = client.get("/api/v1/connectome/neurons/99999999")
    assert response.status_code == 404


def test_api_upstream_and_downstream_endpoints():
    """Test upstream and downstream partner API routes."""
    resp_up = client.get("/api/v1/connectome/neurons/10234/upstream?min_synapses=5")
    assert resp_up.status_code == 200
    assert resp_up.json()["count"] >= 2

    resp_down = client.get("/api/v1/connectome/neurons/10234/downstream?min_synapses=5")
    assert resp_down.status_code == 200
    assert resp_down.json()["count"] >= 2


def test_api_connectivity_post_endpoint():
    """Test POST /api/v1/connectome/connectivity endpoint."""
    payload = {
        "source_ids": [10005, 10006],
        "target_ids": [10234],
        "min_synapses": 10,
    }
    response = client.post("/api/v1/connectome/connectivity", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 2
    for c in data["connections"]:
        assert c["post_body_id"] == 10234
