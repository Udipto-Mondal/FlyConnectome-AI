"""
Automated Integration Tests for NeuroGraph AI FastAPI Endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "graph_statistics" in data


def test_presets_endpoint():
    response = client.get("/api/presets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    preset_ids = [p["id"] for p in data]
    assert "preset_visual_escape" in preset_ids


def test_discovery_endpoint():
    payload = {"query": "Find the visual escape circuit when a looming threat is detected"}
    response = client.post("/api/discover", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "plan" in data
    assert "graph" in data
    assert "literature" in data
    assert "report" in data
    assert len(data["agent_timeline"]) == 4


def test_ablation_endpoint():
    payload = {
        "silenced_ids": ["10234"],
        "source_ids": ["10005"],
        "target_ids": ["20145"]
    }
    response = client.post("/api/ablate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "severance_percentage" in data
    assert data["severance_percentage"] > 0
