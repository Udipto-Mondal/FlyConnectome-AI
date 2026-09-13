"""
Data models and schemas for the Drosophila Male CNS connectome dataset (Male CNS v1.0).
Provides strict, validated Pydantic types for neurons, synaptic connections, ROIs,
and scientific provenance records.
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class NeuronModel(BaseModel):
    """
    Schema for a reconstructed biological neuron in the Male CNS connectome.
    Directly aligns with Janelia / Google Research neuPrint schema.
    """
    body_id: int = Field(..., description="Unique Janelia reconstruction body ID")
    instance: Optional[str] = Field(None, description="Named neuron instance (e.g. GF_L, LC4)")
    type: Optional[str] = Field(None, description="Cell type classification (e.g. Giant Fiber)")
    status: Optional[str] = Field(None, description="Proofreading status (e.g. Traced)")
    size: Optional[int] = Field(None, description="Volume of reconstructed skeleton in voxels")
    pre: Optional[int] = Field(0, description="Total presynaptic T-bar count")
    post: Optional[int] = Field(0, description="Total postsynaptic polyadic contact count")
    soma_neuropil: Optional[str] = Field(None, description="Neuropil ROI containing cell body")
    neurotransmitter: Optional[str] = Field(None, description="Predicted or verified neurotransmitter")
    coords: Optional[List[float]] = Field(None, description="Spatial centroid [x, y, z] in nanometers")


class SynapticConnectionModel(BaseModel):
    """
    Schema for a verified directed synaptic connection between two neurons.
    """
    pre_body_id: int = Field(..., description="Source presynaptic neuron body ID")
    post_body_id: int = Field(..., description="Target postsynaptic neuron body ID")
    weight: int = Field(..., ge=1, description="Number of verified synaptic contacts (T-bars)")
    roi: Optional[str] = Field(None, description="Neuropil region of interest where synapse occurs")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Proofreading confidence")


class ProvenanceRecord(BaseModel):
    """
    Immutable provenance record tracking query origin, timestamp, and dataset version.
    Mandatory for all scientific discoveries in FlyConnectome AI.
    """
    provenance_id: str = Field(..., description="Unique query execution identifier")
    dataset_name: str = Field("cns", description="Canonical dataset name")
    dataset_version: str = Field("v1.0", description="Dataset release version")
    data_provider: str = Field("Janelia Research Campus / Google Research", description="Source organization")
    query_type: str = Field(..., description="Type of query (cypher, neuron_lookup, connectivity)")
    query_payload: Optional[str] = Field(None, description="Original query text or Cypher command")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Query execution timestamp")
    latency_ms: float = Field(..., description="Execution time in milliseconds")
    is_cached: bool = Field(False, description="Whether the result was served from local disk cache")
    is_live: bool = Field(False, description="Whether the result was retrieved from live neuPrint API")
    source_url: str = Field("https://neuprint.janelia.org", description="Data server endpoint")


class ConnectomeHealthStatus(BaseModel):
    """
    Live health and connectivity status of the Male CNS connectome integration.
    """
    connected: bool = Field(..., description="Whether the neuPrint server responded")
    server: str = Field(..., description="neuPrint server URL")
    dataset: str = Field(..., description="Target dataset (e.g. cns)")
    api_version: Optional[str] = Field(None, description="neuPrint backend API version")
    authenticated: bool = Field(..., description="Whether a valid auth token is configured")
    latency_ms: Optional[float] = Field(None, description="Server round-trip latency in milliseconds")
    message: str = Field(..., description="Human-readable status or diagnostic instruction")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
