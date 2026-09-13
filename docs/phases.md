# FlyConnectome AI — Development Roadmap & Phase Status

This document tracks the phased engineering progression of **FlyConnectome AI** in strict accordance with the Master Development Plan.

---

## Phase Overview & Current Status

| Phase | Title | Status | Primary Focus |
| :---: | :--- | :---: | :--- |
| **0** | **Project Architecture & Foundation** | **COMPLETE** | Repository foundation, config, health endpoints, documentation, testing setup |
| **1** | **Real Male CNS Connectome Integration** | **COMPLETE** | neuPrint API client, official Male CNS v1.0 data schemas, authentication |
| **2** | **Connectome Query Layer** | **COMPLETE** | Type-safe neuron lookups, synaptic edge queries, ROI spatial filters |
| **3** | **Graph Engine & Graph Algorithms** | **COMPLETE** | Directed graph traversals, Dijkstra weighted distance, centrality metrics |
| **4** | Graph-RAG Retrieval System | *Planned* | Subgraph extraction, relevance scoring, connectome context formatting |
| **5** | Planner Agent & Orchestrator | *Planned* | Query decomposition, hypothesis generation, stateful LangGraph pipeline |
| **6** | Literature Agent | *Planned* | Europe PMC & PubMed API integration, citation verification, paper retrieval |
| **7** | Scientific Synthesis Agent | *Planned* | Tripartite evidence aggregation (Connectome, Literature, Inference) |
| **8** | In-Silico Ablation & Graph Perturbation | *Planned* | Node/edge lesion simulation, path severance, vulnerability metrics |
| **9** | Interactive 3D Circuit Visualization | *Planned* | WebGL/Three.js spatial neuropil rendering, interactive inspection |
| **10** | End-to-End Agentic Workflow | *Planned* | Integration of query -> discovery -> ablation -> report -> 3D view |
| **11** | Testing, Provenance & Failure Handling | *Planned* | Scientific validation, edge cases, error recovery, benchmark queries |
| **12** | Dockerization & Release Packaging | *Planned* | Production containers, CI/CD, documentation polishing, public release |

---

## Phase 0: Project Architecture and Repository Foundation

### Objectives
- Establish clean modular directory layout separating backend, frontend, documentation, and tests.
- Create typed configuration management with Pydantic and `.env.example`.
- Establish comprehensive architectural blueprints and scientific data dictionaries in `docs/`.
- Provide foundational FastAPI health (`/api/health`, `/api/v1/health`) and information (`/api/info`) endpoints.
- Establish automated pytest test suite for configuration and foundational services.
- Clean and update `README.md` to truthfully describe the current state without unsubstantiated claims.

### Exit Criteria
- [x] Repository audit completed and documented.
- [x] Environment configuration template (`.env.example`) created.
- [x] Configuration schema (`backend/app/config.py`) refactored.
- [x] Documentation (`docs/architecture.md`, `docs/phases.md`, `docs/data_dictionary.md`) created.
- [x] Backend test suite passing 100%.
- [x] Honest README updated.
- [x] User review and approval obtained before Phase 1.

---

## Phase 1: Real Male CNS Connectome Integration

### Objectives
- Integrate with official Janelia neuPrint API (`https://neuprint.janelia.org`) and install `neuprint-python`.
- Establish type-safe Pydantic models for real Male CNS connectome data (`NeuronModel`, `SynapticConnectionModel`, `ProvenanceRecord`, `ConnectomeHealthStatus`).
- Implement `NeuPrintClient` with authentication handling, live health pinging, Cypher query execution, and disk caching.
- Enforce strict scientific failure transparency: unauthenticated or failing queries return explicit provenance without returning fake data.
- Wire live connectome health status to `/api/health`, `/api/v1/health`, and `/api/v1/connectome/status`.
- Provide automated unit and integration tests for connectome client, models, and API endpoints.

### Exit Criteria
- [x] `NeuPrintClient` implemented with live health check against `https://neuprint.janelia.org/api/version`.
- [x] Pydantic schemas created in `backend/app/connectome/models.py`.
- [x] Cypher query execution with local caching and provenance tracking implemented.
- [x] Dedicated `/api/v1/connectome/status` endpoint functional.
- [x] Subsystem health status updated in `/api/health`.
- [x] Automated test suite passing (25/25 tests).
- [x] User review and approval obtained before Phase 2.

---

## Phase 2: Connectome Query Layer

### Objectives
- Build `ConnectomeQueryLayer` on top of `NeuPrintClient` to abstract connectome Cypher queries into type-safe Python methods.
- Provide single neuron lookups by Janelia body ID, returning validated `NeuronModel` with provenance.
- Support neuron search across cell type, instance name, body ID, and innervated neuropil ROI.
- Implement upstream (presynaptic) and downstream (postsynaptic) partner extraction with minimum synaptic contact thresholds (`min_synapses`).
- Support querying direct synaptic connectivity between sets of candidate source and target neurons.
- Build canonical circuit cache (`data/cache/connectome/canonical_male_cns_circuits.json`) from official Male CNS v1.0 data for reproducible offline tests.
- Expose REST API routes under `/api/v1/connectome/`:
  - `GET /api/v1/connectome/neurons`
  - `GET /api/v1/connectome/neurons/{body_id}`
  - `GET /api/v1/connectome/neurons/{body_id}/upstream`
  - `GET /api/v1/connectome/neurons/{body_id}/downstream`
  - `POST /api/v1/connectome/connectivity`
- Establish comprehensive test coverage (37 automated tests passing).

### Exit Criteria
- [x] `ConnectomeQueryLayer` implemented and exported in `app.connectome`.
- [x] Upstream and downstream partner queries operational with synaptic thresholds.
- [x] Multi-neuron connectivity query operational.
- [x] Canonical Male CNS circuit fixtures created for reproducible offline verification.
- [x] REST API endpoints mounted under `/api/v1/connectome`.
- [x] Automated test suite passing (37/37 tests).
- [x] User review and approval obtained before Phase 3.

---

## Phase 3: Graph Engine & Graph Algorithms

### Objectives
- Build high-performance NetworkX directed graph engine (`ConnectomeGraphEngine`) with biological distance formulations.
- Implement biological distance metric where edge weight represents inverted synaptic resistance ($d(u,v) = \frac{1000}{\max(1, w_{synapses})}$), ensuring high-synapse channels are prioritized in Dijkstra shortest paths.
- Provide multi-source to multi-target directed traversals with both Dijkstra and all simple paths options.
- Implement network centrality analysis: Betweenness Centrality ($C_B(v)$) for bottleneck identification, Closeness Centrality ($C_C(v)$), directed PageRank flow, and synaptic degree metrics.
- Implement mathematically rigorous in-silico circuit ablation adhering strictly to `docs/architecture.md` Section 5:
  - Perturbed graph $G' = (V \setminus S, E')$
  - Reachable Target Loss ($L_{target}$)
  - Path Severance Percentage ($P_{sev}$)
  - Throughput Loss ($T_{loss}$)
  - Composite Vulnerability Score ($V \in [0.0, 10.0]$)
  - Surviving polysynaptic detours identification
- Package induced subgraphs with 3D centroid coordinates (`coords`), degrees, and edge synapses for WebGL/Three.js rendering.
- Calculate global graph topological invariants (density, reciprocity, strongly/weakly connected components, DAG evaluation).
- Expose REST API endpoints under `/api/v1/graph/`:
  - `POST /api/v1/graph/paths`
  - `POST /api/v1/graph/centrality`
  - `POST /api/v1/graph/subgraph`
  - `POST /api/v1/graph/ablation`
  - `GET /api/v1/graph/topology`
  - `GET /api/v1/graph/statistics`
- Enforce Tier C Computational Inference provenance tracking (`ComputationalProvenanceRecord`).
- Maintain 100% backward compatibility with Phase 0/1/2 endpoints and tests.

### Exit Criteria
- [x] `ConnectomeGraphEngine` updated and exported in `app.graph`.
- [x] Type-safe Pydantic models implemented in `backend/app/graph/models.py`.
- [x] Dijkstra biological inverted distance pathfinding implemented and tested.
- [x] Betweenness, Closeness, PageRank, and Degree centrality computed with bottleneck detection.
- [x] In-silico ablation engine implementing Section 5 equations ($P_{sev}$, $T_{loss}$, $L_{target}$, $V$).
- [x] Subgraph extraction packaging 3D spatial coordinates ready for WebGL rendering.
- [x] Topological invariants (density, reciprocity, components) operational.
- [x] REST API endpoints mounted under `/api/v1/graph`.
- [x] Automated test suite passing (49/49 tests).
- [ ] User review and approval obtained before Phase 4.

