"""
REST API endpoints for the Connectome Query Layer.
Provides endpoints for neuron lookup, upstream/downstream partners,
and synaptic connectivity queries over the Male CNS connectome.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ....connectome import query_layer, neuprint_client

router = APIRouter(prefix="/connectome", tags=["Connectome"])


class ConnectivityRequest(BaseModel):
    source_ids: List[int] = Field(..., description="List of source presynaptic body IDs")
    target_ids: List[int] = Field(..., description="List of target postsynaptic body IDs")
    min_synapses: int = Field(1, ge=1, description="Minimum synapse threshold")


@router.get("/status")
def get_connectome_status():
    """Check live status and latency of the neuPrint Male CNS connectome server."""
    return neuprint_client.check_health(timeout=6.0).model_dump()


@router.get("/neurons")
def search_neurons(
    query: Optional[str] = Query(None, description="Search term (type, instance name, or body ID)"),
    roi: Optional[str] = Query(None, description="Filter by innervated ROI (e.g. LO, EB, VNC)"),
    limit: int = Query(50, ge=1, le=500, description="Max results to return"),
):
    """Search neurons in the Drosophila Male CNS connectome with provenance."""
    return query_layer.find_neurons(query=query, roi=roi, limit=limit)


@router.get("/neurons/{body_id}")
def get_neuron(body_id: int):
    """Retrieve full metadata for a specific neuron by its Janelia body ID."""
    result = query_layer.get_neuron(body_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Neuron with body_id {body_id} was not found in the Male CNS connectome.",
        )
    return result


@router.get("/neurons/{body_id}/upstream")
def get_upstream_partners(
    body_id: int,
    min_synapses: int = Query(5, ge=1, description="Minimum synaptic contacts threshold"),
    limit: int = Query(50, ge=1, le=500, description="Max connections to return"),
):
    """Retrieve upstream (presynaptic) input partners for a neuron."""
    return query_layer.get_upstream_partners(body_id=body_id, min_synapses=min_synapses, limit=limit)


@router.get("/neurons/{body_id}/downstream")
def get_downstream_partners(
    body_id: int,
    min_synapses: int = Query(5, ge=1, description="Minimum synaptic contacts threshold"),
    limit: int = Query(50, ge=1, le=500, description="Max connections to return"),
):
    """Retrieve downstream (postsynaptic) output partners for a neuron."""
    return query_layer.get_downstream_partners(body_id=body_id, min_synapses=min_synapses, limit=limit)


@router.post("/connectivity")
def get_connectivity(req: ConnectivityRequest):
    """Query direct synaptic connections between a set of source and target neurons."""
    if not req.source_ids or not req.target_ids:
        raise HTTPException(
            status_code=400,
            detail="source_ids and target_ids lists must both contain at least one body ID.",
        )
    return query_layer.get_connectivity(
        source_ids=req.source_ids,
        target_ids=req.target_ids,
        min_synapses=req.min_synapses,
    )
