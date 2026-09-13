"""
Pydantic Data Models and Schemas for NeuroGraph AI Graph Engine (Phase 3).
Provides type-safe models for directed pathfinding, biological distance metrics,
centrality hubs, topological invariants, in-silico ablation, and computational provenance.
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ComputationalProvenanceRecord(BaseModel):
    """
    Tier C: Computational Inference Provenance Record.
    Tracks algorithmic parameters, execution time, and graph dimensionalities.
    """
    provenance_id: str = Field(..., description="Unique computation identifier")
    tier: str = Field("Tier C: Computational Inference", description="Evidence tier classification")
    algorithm: str = Field(..., description="Mathematical algorithm applied")
    node_count: int = Field(..., description="Number of nodes in the analyzed graph/subgraph")
    edge_count: int = Field(..., description="Number of directed edges in the analyzed graph/subgraph")
    latency_ms: float = Field(..., description="Algorithmic execution time in milliseconds")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Execution timestamp")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Input algorithm parameters")


class PathStep(BaseModel):
    """Single directed synaptic step between two neurons."""
    from_id: str = Field(..., description="Presynaptic neuron body ID")
    from_name: str = Field(..., description="Presynaptic neuron instance/type name")
    to_id: str = Field(..., description="Postsynaptic neuron body ID")
    to_name: str = Field(..., description="Postsynaptic neuron instance/type name")
    synapses: int = Field(..., ge=1, description="Number of synaptic contacts")
    biological_distance: float = Field(..., description="Inverted synaptic resistance weight d(u,v)")
    type: Optional[str] = Field("chemical", description="Synapse transmission type (chemical/electrical)")
    roi: Optional[str] = Field(None, description="Neuropil ROI region where connection occurs")


class CircuitPathway(BaseModel):
    """Complete directed neural pathway from a sensory/upstream neuron to motor/downstream target."""
    nodes: List[Dict[str, Any]] = Field(..., description="List of neuron metadata dictionaries along the path")
    node_names: List[str] = Field(..., description="Ordered list of neuron names")
    node_ids: List[str] = Field(..., description="Ordered list of neuron body IDs")
    steps: List[PathStep] = Field(..., description="Directed steps along the pathway")
    total_synapses: int = Field(..., ge=0, description="Sum of all synaptic contacts along the path")
    bottleneck_synapses: int = Field(..., ge=0, description="Minimum synaptic weight along the path (flow limiter)")
    cumulative_biological_distance: float = Field(..., description="Sum of biological resistance distances")
    hops: int = Field(..., ge=1, description="Number of synaptic hops (edges)")


class PathSearchRequest(BaseModel):
    """Request payload for finding pathways between source and target neuron sets."""
    source_ids: List[str] = Field(..., min_length=1, description="Source presynaptic neuron IDs or names")
    target_ids: List[str] = Field(..., min_length=1, description="Target postsynaptic neuron IDs or names")
    algorithm: str = Field("dijkstra", description="Path algorithm: 'dijkstra' (weighted shortest) or 'all_simple'")
    max_depth: int = Field(5, ge=1, le=10, description="Maximum path search depth (hops)")
    cutoff_paths: int = Field(8, ge=1, le=50, description="Maximum number of pathways to return")
    min_synapses: int = Field(1, ge=1, description="Minimum synaptic contacts per edge")
    weight_metric: str = Field(
        "biological_distance",
        description="Path optimization metric: 'biological_distance' (inverted weight) or 'synapses' (raw strength)"
    )


class PathSearchResponse(BaseModel):
    """Response containing discovered neural circuit pathways and bottleneck hubs."""
    paths: List[CircuitPathway] = Field(..., description="Ranked circuit pathways")
    total_pathways_found: int = Field(..., description="Total candidate pathways discovered")
    sources: List[Dict[str, Any]] = Field(..., description="Resolved source neurons")
    targets: List[Dict[str, Any]] = Field(..., description="Resolved target neurons")
    bottlenecks: List[Dict[str, Any]] = Field(..., description="Identified bottleneck neurons along active routes")
    provenance: ComputationalProvenanceRecord


class CentralityRequest(BaseModel):
    """Request payload for computing network centrality on the connectome."""
    node_ids: Optional[List[str]] = Field(None, description="Subset of node IDs to analyze (None = whole graph)")
    metrics: List[str] = Field(
        default=["betweenness", "closeness", "pagerank", "degree"],
        description="Centrality metrics to calculate"
    )


class NodeCentrality(BaseModel):
    """Centrality metrics for an individual neuron."""
    node_id: str = Field(..., description="Neuron body ID")
    name: str = Field(..., description="Neuron instance or type name")
    type: Optional[str] = Field(None, description="Cell type classification")
    neuropil: Optional[str] = Field(None, description="Primary neuropil ROI")
    betweenness_centrality: Optional[float] = Field(None, description="Betweenness centrality bottleneck score")
    closeness_centrality: Optional[float] = Field(None, description="Closeness centrality score")
    pagerank: Optional[float] = Field(None, description="Directed PageRank influence score")
    in_degree: int = Field(0, description="Number of incoming synaptic edges")
    out_degree: int = Field(0, description="Number of outgoing synaptic edges")
    in_synapses: int = Field(0, description="Sum of incoming presynaptic T-bar contacts")
    out_synapses: int = Field(0, description="Sum of outgoing postsynaptic contacts")


class CentralityResponse(BaseModel):
    """Response payload for centrality analysis."""
    nodes: List[NodeCentrality] = Field(..., description="Centrality metrics for evaluated neurons")
    top_bottlenecks: List[NodeCentrality] = Field(..., description="Top bottleneck hubs ranked by betweenness")
    provenance: ComputationalProvenanceRecord


class SubgraphNode(BaseModel):
    """Neuron node schema formatted for 2D/3D WebGL circuit rendering."""
    id: str = Field(..., description="Neuron body ID")
    name: str = Field(..., description="Neuron instance/type name")
    type: Optional[str] = Field(None, description="Cell type classification")
    neuropil: Optional[str] = Field(None, description="Neuropil ROI")
    subsystem: Optional[str] = Field(None, description="Functional neural subsystem")
    neurotransmitter: Optional[str] = Field(None, description="Predicted or verified neurotransmitter")
    coords: Optional[List[float]] = Field(None, description="3D spatial centroid [x, y, z]")
    sex_dimorphic: bool = Field(False, description="Whether neuron is sexually dimorphic (e.g. fru+)")
    in_degree: int = Field(0, description="Incoming edge count")
    out_degree: int = Field(0, description="Outgoing edge count")


class SubgraphEdge(BaseModel):
    """Synaptic edge schema formatted for 2D/3D WebGL circuit rendering."""
    source: str = Field(..., description="Presynaptic neuron ID")
    target: str = Field(..., description="Postsynaptic neuron ID")
    synapses: int = Field(..., ge=1, description="Number of verified synaptic contacts")
    biological_distance: float = Field(..., description="Inverted resistance weight")
    type: Optional[str] = Field("chemical", description="Synaptic transmission type")
    roi: Optional[str] = Field(None, description="Neuropil ROI where synapse occurs")


class SubgraphExtractionRequest(BaseModel):
    """Request payload for extracting an induced circuit subgraph."""
    node_ids: List[str] = Field(..., min_length=1, description="Seed neuron IDs or names")
    expand_hops: int = Field(0, ge=0, le=3, description="Radius of k-hop neighborhood expansion")
    min_synapses: int = Field(1, ge=1, description="Minimum synapse threshold for included edges")


class SubgraphExtractionResponse(BaseModel):
    """Extracted induced circuit subgraph ready for 3D Three.js rendering."""
    nodes: List[SubgraphNode] = Field(..., description="List of nodes with 3D coordinates")
    edges: List[SubgraphEdge] = Field(..., description="List of directed synaptic connections")
    node_count: int = Field(..., description="Total nodes in subgraph")
    edge_count: int = Field(..., description="Total edges in subgraph")
    total_synapses: int = Field(..., description="Total synaptic contacts across all edges")
    provenance: ComputationalProvenanceRecord


class AblationRequestV2(BaseModel):
    """Request payload for in-silico circuit ablation."""
    silenced_ids: List[str] = Field(..., min_length=1, description="Neuron IDs to silence/knockout")
    source_ids: Optional[List[str]] = Field(None, description="Sensory/input neuron IDs to evaluate transmission from")
    target_ids: Optional[List[str]] = Field(None, description="Motor/output neuron IDs to evaluate transmission to")
    max_depth: int = Field(6, ge=1, le=10, description="Maximum pathway search depth")


class AblationResponseV2(BaseModel):
    """Mathematical in-silico ablation results conforming to docs/architecture.md Section 5."""
    silenced_neurons: List[Dict[str, Any]] = Field(..., description="Metadata of knocked out neurons")
    baseline_paths_count: int = Field(..., description="Number of functional pathways in intact graph K(G)")
    ablated_paths_count: int = Field(..., description="Number of functional pathways remaining in perturbed graph K(G')")
    severance_percentage: float = Field(..., ge=0.0, le=100.0, description="Path Severance Percentage P_sev")
    baseline_throughput: int = Field(..., description="Baseline synaptic flow capacity W_flow(G)")
    ablated_throughput: int = Field(..., description="Ablated synaptic flow capacity W_flow(G')")
    throughput_loss_percentage: float = Field(..., ge=0.0, le=100.0, description="Throughput Loss Percentage T_loss")
    baseline_reachable_targets: int = Field(..., description="Reachable target neurons in intact graph")
    ablated_reachable_targets: int = Field(..., description="Reachable target neurons in ablated graph")
    target_loss_percentage: float = Field(..., ge=0.0, le=100.0, description="Reachable Target Loss L_target")
    is_completely_severed: bool = Field(..., description="True if no pathways survive ablation")
    vulnerability_score: float = Field(..., ge=0.0, le=10.0, description="Composite vulnerability score (0.0 to 10.0)")
    alternative_detours: List[Dict[str, Any]] = Field(..., description="Surviving polysynaptic bypass pathways")
    scientific_explanation: str = Field(..., description="Formal computational interpretation")
    provenance: ComputationalProvenanceRecord


class GraphTopologyResponse(BaseModel):
    """Global topological invariants of the connectome directed graph."""
    node_count: int = Field(..., description="Total vertices |V|")
    edge_count: int = Field(..., description="Total directed edges |E|")
    total_synapses: int = Field(..., description="Sum of all synaptic contacts")
    is_directed: bool = Field(True, description="Whether the graph is directed")
    density: float = Field(..., description="Graph density |E| / (|V|*(|V|-1))")
    reciprocity: float = Field(..., description="Fraction of reciprocal connections (bidirectional edges)")
    strongly_connected_components: int = Field(..., description="Count of strongly connected components")
    weakly_connected_components: int = Field(..., description="Count of weakly connected components")
    is_dag: bool = Field(..., description="Whether the graph is a Directed Acyclic Graph")
    average_degree: float = Field(..., description="Average node degree")
    subsystem_distribution: Dict[str, int] = Field(..., description="Neuron distribution by functional subsystem")
    provenance: ComputationalProvenanceRecord
