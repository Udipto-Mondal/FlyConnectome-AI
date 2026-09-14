"""
REST API Endpoints for Graph-RAG Retrieval System (Phase 4).
Exposes endpoints for:
- Query-based circuit retrieval with multi-factor relevance ranking
- Connectome context formatting for downstream LLM agents
- Pathway scoring against natural language specifications
- Subsystem capability and status diagnostics
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ....graph_rag import (
    GraphRAGQueryRequest,
    GraphRAGRetrievalResponse,
    GraphRAGContext,
    RelevanceScoreBreakdown,
    graph_rag_retriever,
    circuit_scorer,
    context_formatter,
)
from ....graph.engine import graph_engine
from ....config import settings

router = APIRouter(tags=["Graph-RAG Retrieval (Phase 4)"])


class PathScoringRequest(BaseModel):
    node_ids: List[str] = Field(..., min_length=2, description="Ordered node IDs in circuit pathway")
    total_synapses: Optional[int] = Field(None, description="Optional total synapse count (auto-computed if omitted)")
    query: str = Field("", description="Neuroscience query to evaluate against")
    target_rois: Optional[List[str]] = Field(None, description="Target neuropil ROIs")
    target_neurotransmitters: Optional[List[str]] = Field(None, description="Target neurotransmitters")


class DirectContextFormatRequest(BaseModel):
    node_ids: List[str] = Field(..., min_length=1, description="Participating neuron body IDs")
    query: str = Field("Direct Subgraph Inspection", description="Context query description")
    token_budget: int = Field(2500, ge=500, le=16000, description="Token budget cap")


@router.get("/status")
def get_graph_rag_status():
    """Diagnostic status and configuration for the Graph-RAG Retrieval System."""
    return {
        "status": "operational",
        "subsystem": "Graph-RAG Retrieval System",
        "phase": "Phase 4",
        "version": settings.VERSION,
        "default_depth": settings.GRAPH_RAG_MAX_DEPTH,
        "default_min_synapses": settings.GRAPH_RAG_MIN_SYNAPSES,
        "default_token_budget": settings.GRAPH_RAG_DEFAULT_TOKEN_BUDGET,
        "capabilities": [
            "Entity grounding across cell types, instances, and neuropils",
            "Directed multigraph path traversal with biological resistance metrics",
            "Multi-factor relevance scoring (Synapse, Distance, Centrality, Query)",
            "Anti-hallucination Tier A LLM context serialization",
            "Token budget optimization and truncation handling",
        ],
    }


@router.post("/retrieve", response_model=GraphRAGRetrievalResponse)
def retrieve_circuit_context(request: GraphRAGQueryRequest):
    """
    Execute end-to-end Graph-RAG retrieval:
    Resolves biological entities from query, traverses connectome multigraph,
    ranks candidate circuits with multi-factor scoring, and serializes prompt context.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")
    try:
        return graph_rag_retriever.retrieve(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph-RAG retrieval failure: {str(e)}")


@router.post("/score-path", response_model=RelevanceScoreBreakdown)
def score_circuit_pathway(req: PathScoringRequest):
    """
    Compute multi-factor biological relevance score for a given circuit pathway.
    """
    resolved_nodes = graph_engine.resolve_neuron_ids(req.node_ids)
    if len(resolved_nodes) < 2:
        raise HTTPException(status_code=400, detail="Must provide at least 2 resolvable neuron IDs in pathway.")

    # Calculate actual path metrics from graph if not provided
    total_syn = req.total_synapses
    bottleneck_syn = 10
    bio_dist = 0.0

    if total_syn is None:
        total_syn = 0
        weights = []
        for u, v in zip(resolved_nodes[:-1], resolved_nodes[1:]):
            if graph_engine.graph.has_edge(u, v):
                w = graph_engine.graph[u][v].get("weight", 1)
            else:
                w = 1
            weights.append(w)
            total_syn += w
            bio_dist += 1000.0 / max(1, w)
        bottleneck_syn = min(weights) if weights else 1
    else:
        bio_dist = 1000.0 / max(1, total_syn // max(1, len(resolved_nodes) - 1))

    node_names = [
        graph_engine.get_neuron(nid).get("name", nid) if graph_engine.get_neuron(nid) else nid
        for nid in resolved_nodes
    ]

    return circuit_scorer.score_pathway(
        node_ids=resolved_nodes,
        node_names=node_names,
        total_synapses=total_syn,
        biological_distance=bio_dist,
        bottleneck_synapses=bottleneck_syn,
        graph=graph_engine.graph,
        node_metadata=graph_engine.neuron_lookup,
        query=req.query,
        target_rois=req.target_rois,
        target_neurotransmitters=req.target_neurotransmitters,
    )


@router.post("/format-context", response_model=GraphRAGContext)
def format_direct_context(req: DirectContextFormatRequest):
    """
    Extract and compile prompt-ready LLM context for an explicit set of neuron IDs.
    """
    resolved_ids = graph_engine.resolve_neuron_ids(req.node_ids)
    if not resolved_ids:
        raise HTTPException(status_code=400, detail="None of the specified neuron IDs could be resolved.")

    from ....graph.models import SubgraphExtractionRequest
    sub_res = graph_engine.extract_subgraph_v2(
        SubgraphExtractionRequest(
            node_ids=resolved_ids,
            expand_hops=0,
            min_synapses=1,
            include_3d_coordinates=True
        )
    )

    return context_formatter.format_context(
        nodes=sub_res.nodes,
        edges=sub_res.edges,
        ranked_pathways=[],
        query=req.query,
        token_budget=req.token_budget,
    )
