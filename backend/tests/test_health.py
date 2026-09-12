"""
Phase 0 Automated Tests for NeuroGraph AI Health & Foundation Endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)


def test_root_endpoint_metadata():
    """Verify root endpoint returns valid platform metadata and Phase 0 status."""
    response = client.get("/", headers={"accept": "application/json"})
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "NeuroGraph AI"
    assert data["phase"] == "Phase 0 — Foundation"
    assert data["status"] == "operational"
    assert "endpoints" in data
    assert data["endpoints"]["health"] == "/api/health"
    assert data["endpoints"]["info"] == "/api/info"


def test_health_endpoint():
    """Verify /api/health returns operational status and subsystem diagnostics."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["platform"] == settings.PROJECT_NAME
    assert data["phase"] == "Phase 0 — Foundation"
    assert "subsystems" in data
    assert data["subsystems"]["api"] == "operational"
    assert data["subsystems"]["configuration"] == "valid"
    assert "timestamp" in data


def test_v1_health_endpoint():
    """Verify /api/v1/health is consistent with /api/health."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["phase"] == settings.PHASE


def test_platform_info_endpoint():
    """Verify /api/info returns architectural metadata and roadmap."""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "NeuroGraph AI"
    assert "Drosophila Male CNS" in data["source_of_truth"]
    assert len(data["evidence_tiers"]) == 3
    assert "Tier A" in data["evidence_tiers"][0]
    assert "Tier B" in data["evidence_tiers"][1]
    assert "Tier C" in data["evidence_tiers"][2]
    assert data["roadmap"]["current_phase"] == "Phase 0 — Project Architecture and Repository Foundation"
    assert data["roadmap"]["next_phase"] == "Phase 1 — Real Male CNS Connectome Integration"
