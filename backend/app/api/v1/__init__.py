"""
API v1 package for FlyConnectome AI.
Mounts connectome query layer and Phase 3 graph engine routers.
"""

from fastapi import APIRouter
from .endpoints.connectome import router as connectome_router
from .endpoints.graph import router as graph_router

api_v1_router = APIRouter(prefix="/v1")
api_v1_router.include_router(connectome_router)
api_v1_router.include_router(graph_router)

__all__ = ["api_v1_router"]
