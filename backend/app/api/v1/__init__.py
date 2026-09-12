"""
API v1 package for NeuroGraph AI.
"""

from fastapi import APIRouter
from .endpoints.connectome import router as connectome_router

api_v1_router = APIRouter(prefix="/v1")
api_v1_router.include_router(connectome_router)

__all__ = ["api_v1_router"]
