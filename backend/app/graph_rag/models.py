"""
Pydantic Data Models for Graph-RAG Retrieval System (Phase 4).
Defines schemas for biological entity grounding, multi-factor circuit relevance scoring,
LLM connectome context formatting, and retrieval payloads.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from ..graph.models import SubgraphNode, SubgraphEdge, ComputationalProvenanceRecord


class RelevanceScoreBreakdown(BaseModel):
    """
    Multi-factor relevance breakdown for candidate neural circuits.
    Normalized rigorously to [0.0, 1.0].
    """
    synaptic_weight_score: float = Field(..., ge=0.0, le=1.0, description="Contact abundance & bottleneck throughput capacity")
    biological_distance_score: float = Field(..., ge=0.0, le=1.0, description="Shortest path efficiency via inverted resistance formulation")
    centrality_hub_score: float = Field(..., ge=0.0, le=1.0, description="Betweenness & PageRank hubness of intermediate interneurons")
    query_alignment_score: float = Field(..., ge=0.0, le=1.0, description="Lexical and semantic alignment with query, ROIs, and neurotransmitters")
    composite_score: float = Field(..., ge=0.0, le=1.0, description="Weighted composite score R in [0.0, 1.0]")
    ranking_rationale: str = Field(..., description="Explainable scientific rationale for the computed relevance")


class ScoredPathway(BaseModel):
    """
    A biologically validated circuit pathway paired with its mathematical relevance score.
    """
    path_id: str = Field(..., description="Unique deterministic identifier for pathway")
    node_ids: List[str] = Field(..., description="Ordered list of neuron IDs from source to target")
    node_names: List[str] = Field(..., description="Ordered human-readable neuron names/instances")
    total_synapses: int = Field(..., ge=0, description="Cumulative synaptic contacts across pathway")
    biological_distance: float = Field(..., ge=0.0, description="Inverted resistance metric sum (1000 / w_uv)")
    bottleneck_synapses: int = Field(..., ge=0, description="Synaptic count of the rate-limiting bottleneck edge")
    bottleneck_edge: Optional[List[str]] = Field(None, description="[pre_id, post_id] of rate-limiting connection")
    score: RelevanceScoreBreakdown = Field(..., description="Relevance score breakdown")


class GraphRAGQueryRequest(BaseModel):
    """
    Input request for Graph-RAG circuit retrieval.
    Accepts free-form natural language query alongside optional structured constraints.
    """
    query: str = Field(..., min_length=1, description="Neuroscience inquiry or circuit description")
    seed_neuron_ids: Optional[List[str]] = Field(default_factory=list, description="Optional seed neuron IDs / instances")
    source_neuron_ids: Optional[List[str]] = Field(default_factory=list, description="Candidate sensory/input neuron IDs")
    target_neuron_ids: Optional[List[str]] = Field(default_factory=list, description="Candidate motor/output neuron IDs")
    neuropil_rois: Optional[List[str]] = Field(default_factory=list, description="Neuropil spatial constraints (e.g. GNG, VNC, AL)")
    neurotransmitters: Optional[List[str]] = Field(default_factory=list, description="Neurotransmitter constraints (e.g. acetylcholine, gaba)")
    max_depth: int = Field(5, ge=1, le=10, description="Maximum synaptic hop depth")
    min_synapses: int = Field(5, ge=1, description="Minimum synaptic contact threshold for traversed edges")
    max_pathways: int = Field(5, ge=1, le=20, description="Maximum number of ranked pathways to return")
    token_budget: int = Field(2500, ge=500, le=16000, description="Token budget cap for formatted LLM context")
    include_markdown_context: bool = Field(True, description="Whether to compile LLM prompt markdown context")


class GraphRAGContext(BaseModel):
    """
    Serialized connectome graph context engineered for downstream LLM reasoning agents.
    Provides strict Tier A factual constraints preventing model hallucination.
    """
    markdown_context: str = Field(..., description="Dense, prompt-ready markdown representation of retrieved circuit")
    dense_graph_summary: Dict[str, Any] = Field(..., description="Structured machine-readable circuit topology")
    total_nodes: int = Field(..., ge=0, description="Number of unique neurons in context")
    total_edges: int = Field(..., ge=0, description="Number of synaptic connections in context")
    token_count_estimate: int = Field(..., ge=0, description="Estimated token count of markdown context (~4 chars per token)")
    tier_a_provenance: List[Dict[str, Any]] = Field(default_factory=list, description="Official Janelia body IDs and dataset tags")


class GraphRAGRetrievalResponse(BaseModel):
    """
    Complete Graph-RAG retrieval payload containing grounded entities, ranked pathways,
    subgraph structure, and LLM-ready context.
    """
    query: str = Field(..., description="Original user research query")
    grounded_entities: Dict[str, Any] = Field(..., description="Biological entities extracted from query")
    nodes: List[SubgraphNode] = Field(..., description="Retrieved neuron nodes with 3D coordinates")
    edges: List[SubgraphEdge] = Field(..., description="Retrieved synaptic connections with contact weights")
    ranked_pathways: List[ScoredPathway] = Field(..., description="Candidate circuit pathways ranked by composite relevance")
    context: GraphRAGContext = Field(..., description="Formatted LLM prompt context")
    provenance: ComputationalProvenanceRecord = Field(..., description="Tier C computational execution provenance")
