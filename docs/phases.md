# NeuroGraph AI — Development Roadmap & Phase Status

This document tracks the phased engineering progression of **NeuroGraph AI** in strict accordance with the Master Development Plan.

---

## Phase Overview & Current Status

| Phase | Title | Status | Primary Focus |
| :---: | :--- | :---: | :--- |
| **0** | **Project Architecture & Foundation** | **In Progress** | Repository foundation, config, health endpoints, documentation, testing setup |
| **1** | Real Male CNS Connectome Integration | *Planned* | neuPrint API client, official Male CNS v1.0 data schemas, authentication |
| **2** | Connectome Query Layer | *Planned* | Type-safe neuron lookups, synaptic edge queries, ROI spatial filters |
| **3** | Graph Engine & Graph Algorithms | *Planned* | Directed graph traversals, Dijkstra weighted distance, centrality metrics |
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
- [ ] User review and approval obtained before Phase 1.
