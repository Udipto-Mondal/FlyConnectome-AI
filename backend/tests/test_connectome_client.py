"""
Phase 1 Automated Tests for Male CNS Connectome Integration.
Tests neuPrint client, data models, authentication handling, and provenance tracking.
"""

import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.connectome.client import NeuPrintClient
from app.connectome.models import (
    NeuronModel,
    SynapticConnectionModel,
    ProvenanceRecord,
    ConnectomeHealthStatus,
)

client = TestClient(app)


def test_client_initialization():
    """Verify NeuPrintClient sets default Male CNS server and dataset parameters."""
    npc = NeuPrintClient(
        server="https://neuprint.janelia.org",
        dataset="cns",
        token="",
    )
    assert npc.server == "https://neuprint.janelia.org"
    assert npc.dataset == "cns"
    assert npc.is_authenticated is False


def test_client_headers_without_token():
    """Verify headers do not include Authorization when token is empty or default placeholder."""
    npc = NeuPrintClient(token="")
    headers = npc._get_headers()
    assert "Authorization" not in headers
    assert "application/json" in headers["Accept"]

    npc_placeholder = NeuPrintClient(token="your_neuprint_auth_token_here")
    headers_placeholder = npc_placeholder._get_headers()
    assert "Authorization" not in headers_placeholder


def test_client_headers_with_token():
    """Verify Authorization Bearer header is included when token is set."""
    npc = NeuPrintClient(token="valid_secret_token_123")
    assert npc.is_authenticated is True
    headers = npc._get_headers()
    assert headers["Authorization"] == "Bearer valid_secret_token_123"


def test_live_health_check():
    """Verify live health check contacts neuPrint public version API."""
    npc = NeuPrintClient(server="https://neuprint.janelia.org", dataset="cns")
    status = npc.check_health(timeout=8.0)
    # neuprint.janelia.org is online and public
    assert isinstance(status, ConnectomeHealthStatus)
    assert status.server == "https://neuprint.janelia.org"
    assert status.dataset == "cns"
    if status.connected:
        assert status.api_version is not None
        assert status.latency_ms is not None
        assert status.latency_ms > 0


def test_unauthenticated_cypher_honest_failure():
    """
    Verify executing Cypher without auth token returns explicit failure,
    preserving provenance and scientific honesty without returning fake data.
    """
    npc = NeuPrintClient(token="")
    result = npc.execute_cypher("MATCH (n:Neuron) RETURN count(n)")
    assert result["error"] == "UNAUTHENTICATED"
    assert "Insufficient connectome evidence" in result["message"]
    assert "NEUPRINT_TOKEN" in result["message"]
    assert "provenance" in result
    assert result["provenance"]["dataset_name"] == "cns"
    assert result["provenance"]["dataset_version"] == "v1.0"
    assert result["data"] is None


def test_neuron_model_validation():
    """Verify NeuronModel correctly validates realistic Male CNS neuron record."""
    neuron_data = {
        "body_id": 10234,
        "instance": "GF_L",
        "type": "Giant Fiber",
        "status": "Traced",
        "size": 3482910,
        "pre": 1240,
        "post": 8420,
        "soma_neuropil": "GNG",
        "neurotransmitter": "acetylcholine",
        "coords": [-15.0, 60.0, 170.0],
    }
    neuron = NeuronModel(**neuron_data)
    assert neuron.body_id == 10234
    assert neuron.instance == "GF_L"
    assert neuron.pre == 1240
    assert neuron.coords == [-15.0, 60.0, 170.0]


def test_synaptic_connection_model_validation():
    """Verify SynapticConnectionModel validates biological synapse records."""
    edge_data = {
        "pre_body_id": 10005,
        "post_body_id": 10234,
        "weight": 48,
        "roi": "LO",
        "confidence": 0.98,
    }
    edge = SynapticConnectionModel(**edge_data)
    assert edge.pre_body_id == 10005
    assert edge.post_body_id == 10234
    assert edge.weight == 48
    assert edge.roi == "LO"


def test_provenance_record():
    """Verify ProvenanceRecord captures dataset version and query metadata."""
    record = ProvenanceRecord(
        provenance_id="prov_test_001",
        dataset_name="cns",
        dataset_version="v1.0",
        query_type="cypher",
        query_payload="MATCH (n) RETURN n LIMIT 1",
        latency_ms=45.2,
        is_cached=False,
        is_live=True,
    )
    assert record.dataset_name == "cns"
    assert record.dataset_version == "v1.0"
    assert record.data_provider == "Janelia Research Campus / Google Research"
    assert record.is_live is True


def test_connectome_api_status_endpoint():
    """Verify /api/v1/connectome/status HTTP endpoint returns valid health status."""
    response = client.get("/api/v1/connectome/status")
    assert response.status_code == 200
    data = response.json()
    assert "connected" in data
    assert data["server"] == "https://neuprint.janelia.org"
    assert data["dataset"] == "cns"
    assert "message" in data


def test_health_endpoint_subsystem_connectome():
    """Verify /api/health now includes the connectome subsystem status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "connectome" in data["subsystems"]
    assert data["phase"] == settings.PHASE
    assert data["version"] == settings.VERSION
