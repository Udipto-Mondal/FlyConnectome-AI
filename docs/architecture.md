# NeuroGraph AI — System Architecture Document

## 1. Executive Summary & Vision

**NeuroGraph AI** is an autonomous, research-oriented agentic scientific platform designed to convert natural-language neuroscience queries into evidence-grounded neural circuit discoveries.

The platform grounds multi-agent reasoning in the **Drosophila Male Central Nervous System (Male CNS v1.0)** connectome dataset, utilizing Graph-RAG (Graph Retrieval-Augmented Generation), mathematical graph traversal algorithms, peer-reviewed literature validation via Europe PMC, and in-silico circuit ablation.

```
                  [ User Neuroscience Question ]
                                 │
                                 ▼
                         [ Planner Agent ]
             (Subsystem identification, sensory/motor targets)
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       [ Connectome Agent ]              [ Literature Agent ]
       (neuPrint Male CNS v1.0)           (Europe PMC / PubMed)
                 │                               │
                 ▼                               │
      [ Subgraph Extraction ]                    │
                 │                               │
                 ▼                               │
      [ Graph Analysis Agent ]                   │
  (Dijkstra, Centrality, Ablation)               │
                 │                               │
                 └───────────────┬───────────────┘
                                 ▼
                     [ Synthesis Agent ]
            (Tripartite Evidence Separation)
                                 │
                                 ▼
                     [ Scientific Report ]
                                 +
              [ Interactive 3D WebGL Circuit ]
                                 +
                   [ In-Silico Ablation ]
```

---

## 2. Core Engineering & Scientific Principles

1. **Evidence Over Assumptions**: The LLM is NEVER the source of truth for neural connectivity. Neural circuits are retrieved from the canonical connectome database.
2. **Real Data Over Demo Data**: Synthetic toy graphs are restricted to local unit tests. Production discoveries are sourced from authoritative connectome repositories (Male CNS v1.0).
3. **Tripartite Evidence Separation**: Scientific outputs must strictly delineate:
   - **Connectome Evidence**: Raw anatomical observations (neuron IDs, synapse counts, neuropil ROIs, graph topology).
   - **Literature Evidence**: Published experimental findings (authors, journal, PMID, DOI, experimental context).
   - **Computational Inference**: Derived computational metrics (shortest paths, bottleneck centrality, in-silico ablation impact).
4. **Reproducibility & Provenance**: Every retrieved neuron, edge, and citation carries metadata detailing the source dataset version, query timestamp, and retrieval parameters.
5. **Honest Failure Transparency**: When connectome data does not support a hypothesized pathway, the system explicitly reports: *"Insufficient connectome evidence was retrieved for this claim."*

---

## 3. Tripartite Evidence Separation Model

To prevent hallucination and maintain peer-review standards, all findings synthesized by NeuroGraph AI are partitioned into three immutable tiers:

| Evidence Tier | Data Types | Source of Truth | Verification Standard |
| :--- | :--- | :--- | :--- |
| **Tier A: Observed Connectome Evidence** | Neuron body IDs, types, polarity, synapse counts, neuropil meshes, reconstructed morphology. | Drosophila Male CNS connectome (v1.0) via neuPrint API. | Exact database match; verified reconstructive provenance. |
| **Tier B: Published Literature Evidence** | Hypotheses, behavioral phenotypes, optogenetic verifications, neurotransmitter assays. | Europe PMC, PubMed API. | Resolvable DOI/PMID with peer-reviewed publication metadata. |
| **Tier C: Computational Inference** | Path rankings, flow centrality, network vulnerability, in-silico knockouts. | Deterministic NetworkX / Graph Engine algorithms. | Documented mathematical equations and statistical significance. |

---

## 4. Multi-Agent Architecture

The discovery engine employs specialized agents coordinated by a stateful Orchestrator:

### 4.1 Planner Agent
- **Input**: Free-form natural language neuroscience inquiry.
- **Output**: Structured `ResearchPlan` (sensory modality, candidate neuropils, motor targets, analysis mode).
- **Constraint**: Must NOT invent biological names or connections; formulates testable connectome queries.

### 4.2 Connectome / Graph-RAG Agent
- **Input**: Query specification from Planner.
- **Output**: Ground-truth subgraphs, verified neuron body IDs, synaptic edge weights, and neuropil coordinates.
- **Constraint**: Direct interface with neuPrint / Male CNS v1.0; no synthetic fallbacks in discovery mode.

### 4.3 Graph Analysis Agent
- **Input**: Extracted connectome subgraph.
- **Output**: Pathway enumerations, bottleneck analysis, shortest/weighted paths, betweenness centrality.
- **Formulation**:
  - Distance metric: Inverted synaptic weight $d(u, v) = \frac{1}{\max(1, w_{synapses})}$
  - Ensures high-synapse biological channels are preferred during path finding.

### 4.4 Literature Agent
- **Input**: Neuron candidates and behavioral context.
- **Output**: Peer-reviewed citations from Europe PMC / PubMed.
- **Constraint**: Discards unsubstantiated web sources; indexes exact DOIs and PMIDs.

### 4.5 Synthesis Agent
- **Input**: Aggregated outputs from Graph Analysis and Literature agents.
- **Output**: Structured scientific report explicitly labeling Tier A, Tier B, and Tier C findings.

### 4.6 Orchestrator
- **Role**: Coordinates the agent lifecycle, manages state checkpoints, handles API rate limits, retries, and formats final API outputs.

---

## 5. In-Silico Ablation Mathematical Formulation

Virtual lesioning is modeled strictly as a computational perturbation on the connectome multigraph $G = (V, E)$.

Given an ablation target set $S \subset V$:
1. **Perturbed Graph**: $G' = (V \setminus S, E')$ where $E' = \{(u, v) \in E \mid u, v \notin S\}$.
2. **Reachable Target Loss ($L_{target}$)**:
   $$L_{target} = \frac{|T_{reach}(G) \setminus T_{reach}(G')|}{|T_{reach}(G)|} \times 100\%$$
3. **Path Severance Percentage ($P_{sev}$)**:
   $$P_{sev} = \frac{K_{paths}(G) - K_{paths}(G')}{K_{paths}(G)} \times 100\%$$
4. **Throughput Loss ($T_{loss}$)**:
   $$T_{loss} = \frac{W_{flow}(G) - W_{flow}(G')}{W_{flow}(G)} \times 100\%$$
   where $W_{flow}(G) = \sum_{p \in K} \min_{(u,v) \in p} w_{uv}$.

*Disclaimer: In-silico ablation results represent computational network perturbations within the analyzed subgraph, not definitive in-vivo physiological proof.*

---

## 6. Technology Stack & Infrastructure

- **Language & Runtime**: Python 3.12+
- **API Framework**: FastAPI, Pydantic v2
- **Graph Computing**: NetworkX, SciPy
- **Connectome Interface**: neuprint-python, neuPrint HTTP REST API
- **Literature Services**: Europe PMC REST API, NCBI E-utilities
- **Frontend Visualization**: Vite, Vanilla CSS, Three.js (WebGL 3D neuropil rendering)
- **Containerization**: Multi-stage Docker, Docker Compose
