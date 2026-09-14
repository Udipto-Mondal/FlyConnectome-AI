"""
Main FastAPI application for FlyConnectome AI.
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
from .connectome import neuprint_client
from .api import api_v1_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous Multi-Agent Graph-RAG for Neural Circuit Discovery."
)

# Mount API v1 router
app.include_router(api_v1_router, prefix="/api")

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
            "ablate": "/api/ablate",
            "graph_rag_retrieve": "/api/v1/graph-rag/retrieve",
            "graph_rag_context": "/api/v1/graph-rag/format-context",
            "graph_rag_status": "/api/v1/graph-rag/status"
        }
    }


@app.get("/api/health")
@app.get("/api/v1/health")
def health_check():
    """System health check and diagnostic status."""
    stats = graph_engine.get_statistics()
    connectome_status = neuprint_client.check_health(timeout=4.0)
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
            "connectome": {
                "connected": connectome_status.connected,
                "server": connectome_status.server,
                "dataset": connectome_status.dataset,
                "authenticated": connectome_status.authenticated,
                "api_version": connectome_status.api_version,
                "message": connectome_status.message
            }
        },
        "graph_statistics": stats
    }


@app.get("/api/v1/connectome/status")
def connectome_status():
    """Detailed live connectivity and authentication status for Male CNS connectome."""
    return neuprint_client.check_health(timeout=6.0).model_dump()


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
        "connectome_interface": "neuprint-python / Janelia neuPrint API (Query Layer Active in Phase 2)",
        "evidence_tiers": [
            "Tier A: Observed Connectome Evidence (Male CNS v1.0 via neuPrint)",
            "Tier B: Published Literature Evidence (Europe PMC / PubMed)",
            "Tier C: Computational Inference (Deterministic Graph Algorithms / In-Silico Ablation)"
        ],
        "roadmap": {
            "current_phase": "Phase 4 — Graph-RAG Retrieval System",
            "next_phase": "Phase 5 — Planner Agent & Orchestrator"
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
    response.headers["X-FlyConnectome-Data-Tier"] = "Phase-0-Synthetic-Fixture"
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
    response.headers["X-FlyConnectome-Data-Tier"] = "Phase-0-Synthetic-Fixture"
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
