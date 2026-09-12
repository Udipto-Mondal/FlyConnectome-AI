"""
Main FastAPI application for NeuroGraph AI.
High-throughput REST and discovery endpoints connecting frontend to Graph-RAG and multi-agent engine.
"""

import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .config import settings
from .graph.engine import graph_engine
from .graph.connectome_data import SHOWCASE_PRESETS, NEURON_DATABASE
from .agents.orchestrator import orchestrator

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous Multi-Agent Graph-RAG & Discovery Engine for the Google Fruit Fly Connectome."
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
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")




class DiscoveryRequest(BaseModel):
    query: str


class AblationRequest(BaseModel):
    silenced_ids: List[str]
    source_ids: Optional[List[str]] = None
    target_ids: Optional[List[str]] = None


@app.get("/")
def root():
    index_file = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "description": "Google Fruit Fly Connectome Multi-Agent Graph-RAG Engine",
        "endpoints": {
            "discover": "/api/discover",
            "ablate": "/api/ablate",
            "presets": "/api/presets",
            "neurons": "/api/neurons",
            "stats": "/api/stats",
            "health": "/api/health"
        }
    }



@app.get("/api/health")
def health_check():
    stats = graph_engine.get_statistics()
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "graph_statistics": stats
    }


@app.get("/api/presets")
def get_presets():
    """Retrieve curated showcase research presets."""
    return SHOWCASE_PRESETS


@app.get("/api/neurons")
def get_neurons(search: Optional[str] = None):
    """Retrieve or search neurons in the connectome database."""
    if search:
        return graph_engine.search_neurons(search)
    return NEURON_DATABASE


@app.get("/api/stats")
def get_stats():
    """Retrieve connectome graph metrics."""
    return graph_engine.get_statistics()


@app.post("/api/discover")
def discover_circuit(req: DiscoveryRequest):
    """
    Run full multi-agent discovery pipeline:
    Planner -> Graph-RAG -> Literature Validation -> Synthesis Report.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        result = orchestrator.run_discovery_pipeline(req.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discovery pipeline error: {str(e)}")


@app.post("/api/ablate")
def run_ablation(req: AblationRequest):
    """
    Simulate in-silico neuronal knockout and calculate circuit severance metrics.
    """
    if not req.silenced_ids:
        raise HTTPException(status_code=400, detail="Must specify at least one neuron ID to silence.")
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
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
