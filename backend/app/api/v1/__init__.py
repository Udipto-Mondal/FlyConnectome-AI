"""
API v1 package for FlyConnectome AI.
Mounts connectome query layer and Phase 3 graph engine routers.
"""

from fastapi import APIRouter
from .endpoints.connectome import router as connectome_router
from .endpoints.graph import router as graph_router
from .endpoints.graph_rag import router as graph_rag_router

api_v1_router = APIRouter(prefix="/v1")
api_v1_router.include_router(connectome_router)
api_v1_router.include_router(graph_router)
api_v1_router.include_router(graph_rag_router, prefix="/graph-rag")

__all__ = ["api_v1_router"]
