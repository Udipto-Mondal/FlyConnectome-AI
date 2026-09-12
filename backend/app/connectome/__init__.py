"""
Connectome package for NeuroGraph AI.
Integrates official Drosophila Male CNS (v1.0) connectome via neuPrint API.
"""

from .models import (
    NeuronModel,
    SynapticConnectionModel,
    ProvenanceRecord,
    ConnectomeHealthStatus,
)
from .client import NeuPrintClient, neuprint_client

__all__ = [
    "NeuronModel",
    "SynapticConnectionModel",
    "ProvenanceRecord",
    "ConnectomeHealthStatus",
    "NeuPrintClient",
    "neuprint_client",
]
