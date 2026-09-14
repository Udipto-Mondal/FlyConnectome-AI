"""
Graph-RAG Package for FlyConnectome AI (Phase 4).
Exports GraphRAGRetriever, CircuitRelevanceScorer, ConnectomeContextFormatter,
and all associated Pydantic models.
"""

from .models import (
    RelevanceScoreBreakdown,
    ScoredPathway,
    GraphRAGQueryRequest,
    GraphRAGContext,
    GraphRAGRetrievalResponse,
)
from .scorer import CircuitRelevanceScorer, circuit_scorer
from .formatter import ConnectomeContextFormatter, context_formatter
from .retriever import GraphRAGRetriever, graph_rag_retriever

__all__ = [
    "RelevanceScoreBreakdown",
    "ScoredPathway",
    "GraphRAGQueryRequest",
    "GraphRAGContext",
    "GraphRAGRetrievalResponse",
    "CircuitRelevanceScorer",
    "circuit_scorer",
    "ConnectomeContextFormatter",
    "context_formatter",
    "GraphRAGRetriever",
    "graph_rag_retriever",
]
