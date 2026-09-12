"""
Main FastAPI application for NeuroGraph AI.
High-throughput REST and discovery endpoints connecting frontend to Graph-RAG and multi-agent engine.
"""

import os
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from .config import settings
from .graph.engine import graph_engine
from .graph.connectome_data import SHOWCASE_PRESETS, NEURON_DATABASE
from .agents.orchestrator import orchestrator

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous Multi-Agent Graph-RAG for Neural Circuit Discovery."
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static frontend if built
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))
if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


class DiscoveryRequest(BaseModel):
    query: str


class AblationRequest(BaseModel):
    silenced_ids: List[str]
    source_ids: Optional[List[str]] = None
    target_ids: Optional[List[str]] = None


@app.get("/")
def root(request: Request):
    """
    Root endpoint. Returns HTML frontend if built and requested by browser,
    otherwise returns platform architectural status and API metadata.
    """
    accept_header = request.headers.get("accept", "")
    index_file = os.path.join(frontend_dist, "index.html")
    if "text/html" in accept_header and os.path.exists(index_file):
        return FileResponse(index_file)

    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "phase": settings.PHASE,
        "status": "operational",
        "description": "Autonomous Multi-Agent Graph-RAG for Neural Circuit Discovery",
        "canonical_dataset": "Drosophila melanogaster Male CNS Connectome (v1.0)",
        "docs_url": "/docs",
        "endpoints": {
            "health": "/api/health",
            "v1_health": "/api/v1/health",
            "info": "/api/info",
            "v1_info": "/api/v1/info",
            "presets": "/api/presets",
            "neurons": "/api/neurons",
            "stats": "/api/stats",
            "discover": "/api/discover",
            "ablate": "/api/ablate"
        }
    }


@app.get("/api/health")
@app.get("/api/v1/health")
def health_check():
    """System health check and diagnostic status."""
    stats = graph_engine.get_statistics()
    return {
        "status": "healthy",
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "phase": settings.PHASE,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subsystems": {
            "api": "operational",
            "configuration": "valid",
            "connectome_source": "Phase 1 Pending (neuPrint Male CNS v1.0)"
        },
        "graph_statistics": stats
    }


@app.get("/api/info")
@app.get("/api/v1/info")
def platform_info():
    """Architectural metadata, current development phase, and provenance specification."""
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "phase": settings.PHASE,
        "environment": settings.ENVIRONMENT,
        "source_of_truth": "Drosophila Male CNS Connectome (v1.0)",
        "connectome_interface": "neuprint-python / Janelia neuPrint API (Scheduled for Phase 1)",
        "evidence_tiers": [
            "Tier A: Observed Connectome Evidence (Male CNS v1.0)",
            "Tier B: Published Literature Evidence (Europe PMC / PubMed)",
            "Tier C: Computational Inference (Deterministic Graph Algorithms / In-Silico Ablation)"
        ],
        "roadmap": {
            "current_phase": "Phase 0 — Project Architecture and Repository Foundation",
            "next_phase": "Phase 1 — Real Male CNS Connectome Integration"
        }
    }


@app.get("/api/presets")
def get_presets():
    """Retrieve curated showcase research presets (Phase 0 development fixture)."""
    return SHOWCASE_PRESETS


@app.get("/api/neurons")
def get_neurons(search: Optional[str] = None):
    """Retrieve or search neurons in the connectome development fixture."""
    if search:
        return graph_engine.search_neurons(search)
    return NEURON_DATABASE


@app.get("/api/stats")
def get_stats():
    """Retrieve connectome graph metrics."""
    return graph_engine.get_statistics()


@app.post("/api/discover")
def discover_circuit(req: DiscoveryRequest, response: Response):
    """
    Run multi-agent discovery pipeline.
    NOTICE: Phase 0 uses synthetic development fixture. Full Male CNS integration occurs in Phase 1-4.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    response.headers["X-NeuroGraph-Data-Tier"] = "Phase-0-Synthetic-Fixture"
    try:
        result = orchestrator.run_discovery_pipeline(req.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discovery pipeline error: {str(e)}")


@app.post("/api/ablate")
def run_ablation(req: AblationRequest, response: Response):
    """
    Simulate in-silico neuronal knockout and calculate circuit severance metrics.
    NOTICE: Phase 0 computational perturbation demo. Formal graph engine ablation is Phase 8.
    """
    if not req.silenced_ids:
        raise HTTPException(status_code=400, detail="Must specify at least one neuron ID to silence.")
    response.headers["X-NeuroGraph-Data-Tier"] = "Phase-0-Synthetic-Fixture"
    try:
        result = graph_engine.simulate_ablation(
            silenced_ids=req.silenced_ids,
            source_ids=req.source_ids,
            target_ids=req.target_ids
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ablation error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
