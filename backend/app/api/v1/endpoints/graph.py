"""
REST API endpoints for the FlyConnectome AI Graph Engine (Phase 3).
Provides high-performance endpoints for:
- Dijkstra weighted shortest paths and multi-hop circuit traversals
- Network centrality analysis (Betweenness bottleneck hubs, Closeness, PageRank)
- Subgraph extraction for 2D/3D WebGL circuit rendering
- In-silico neuronal ablation modeling conforming to docs/architecture.md Section 5
- Global topological invariant metrics and Tier C computational provenance
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from ....graph import (
    graph_engine,
    PathSearchRequest,
    PathSearchResponse,
    CentralityRequest,
    CentralityResponse,
    SubgraphExtractionRequest,
    SubgraphExtractionResponse,
    AblationRequestV2,
    AblationResponseV2,
    GraphTopologyResponse,
)

router = APIRouter(prefix="/graph", tags=["Graph Engine"])


@router.post("/paths", response_model=PathSearchResponse)
def find_circuit_paths(req: PathSearchRequest):
    """
    Compute directed circuit pathways between source and target neuron sets.
    Supports Dijkstra weighted shortest paths (using inverted biological synaptic resistance)
    and all simple paths up to specified depth with synaptic strength filtering.
    """
    if not req.source_ids or not req.target_ids:
        raise HTTPException(
            status_code=400,
            detail="source_ids and target_ids lists must both contain at least one neuron identifier.",
        )
    return graph_engine.find_pathways_v2(req)


@router.post("/centrality", response_model=CentralityResponse)
def compute_graph_centrality(req: CentralityRequest):
    """
    Compute network centrality metrics across the connectome or an induced subgraph.
    Identifies bottleneck hubs via Betweenness Centrality, signal speed via Closeness,
    integrative convergence via directed PageRank, and synaptic degrees.
    """
    return graph_engine.compute_centrality_v2(req)


@router.post("/subgraph", response_model=SubgraphExtractionResponse)
def extract_circuit_subgraph(req: SubgraphExtractionRequest):
    """
    Extract an induced circuit subgraph with 3D spatial centroids and edge synapse weights,
    pre-packaged for WebGL / Three.js 3D neuropil visualization.
    """
    if not req.node_ids:
        raise HTTPException(
            status_code=400,
            detail="node_ids list must contain at least one seed neuron ID.",
        )
    return graph_engine.extract_subgraph_v2(req)


@router.post("/ablation", response_model=AblationResponseV2)
def run_insilico_ablation(req: AblationRequestV2):
    """
    Simulate virtual neuronal ablation / lesioning in-silico.
    Computes Path Severance (P_sev), Throughput Loss (T_loss), Reachable Target Loss (L_target),
    surviving polysynaptic detours, and composite vulnerability scores.
    """
    if not req.silenced_ids:
        raise HTTPException(
            status_code=400,
            detail="Must specify at least one neuron ID to silence.",
        )
    return graph_engine.simulate_ablation_v2(req)


@router.get("/topology", response_model=GraphTopologyResponse)
def get_graph_topology():
    """
    Compute global network topological invariants of the active connectome graph,
    including graph density, reciprocity, strongly/weakly connected components, and DAG status.
    """
    return graph_engine.get_topology_statistics()


@router.get("/statistics")
def get_graph_statistics():
    """
    Retrieve high-level connectome graph metrics and subsystem distributions.
    """
    return graph_engine.get_statistics()
