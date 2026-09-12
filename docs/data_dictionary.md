# NeuroGraph AI — Scientific Data Dictionary (Male CNS Connectome)

## 1. Overview & Source of Truth

The canonical source of truth for neural connectivity in NeuroGraph AI is the **Drosophila melanogaster Male Central Nervous System (Male CNS v1.0)** connectome, released by Janelia Research Campus and Google Research.

The dataset contains the complete central brain and ventral nerve cord (VNC), representing over 160,000 reconstructed neurons and over 120 million synaptic connections.

Access methods:
- **neuPrint API**: High-performance Cypher query interface and REST endpoints hosted at `https://neuprint.janelia.org`.
- **neuprint-python**: Official Python client wrapper for structured pandas/networkx extraction.
- **Direct exports**: Feather/Parquet/Neo4j dumps when local high-throughput querying is required.

---

## 2. Core Entities

### 2.1 Neuron Node Schema

Every neuron node within the NeuroGraph AI graph representation must align with the fields provided by the official dataset:

| Field | Type | Required | Description | Example |
| :--- | :--- | :---: | :--- | :--- |
| `body_id` | `int64` / `str` | **Yes** | Unique Janelia reconstruction identifier. | `10234` |
| `instance` | `str` | No | Specific neuron name/instance if designated. | `GF_L` |
| `type` | `str` | No | Anatomical or functional cell type classification. | `Giant Fiber` |
| `status` | `str` | No | Proofreading and reconstruction confidence status. | `Traced`, `Prelim Roughly Traced` |
| `size` | `int` | No | Total voxel volume of the reconstructed skeleton. | `3482910` |
| `pre` | `int` | No | Presynaptic output site count (T-bars). | `1240` |
| `post` | `int` | No | Postsynaptic input site count (polyadic contacts).| `8420` |
| `soma_neuropil` | `str` | No | Brain/VNC ROI where the cell body resides. | `GNG` (Gnathal Ganglion) |
| `neurotransmitter`| `str` | No | Machine-predicted or verified neurotransmitter. | `acetylcholine`, `gaba`, `glutamate` |
| `coords` | `List[float]` | No | 3D spatial centroid or root coordinate [x, y, z] in nm. | `[-15.0, 60.0, 170.0]` |

### 2.2 Synaptic Connection Edge Schema

Edges represent directed synaptic connectivity between a presynaptic neuron (`pre_neuron`) and a postsynaptic neuron (`post_neuron`):

| Field | Type | Required | Description | Example |
| :--- | :--- | :---: | :--- | :--- |
| `pre_body_id` | `int64` / `str` | **Yes** | Source presynaptic neuron identifier. | `10005` (LC4) |
| `post_body_id`| `int64` / `str` | **Yes** | Target postsynaptic neuron identifier. | `10234` (GF_L) |
| `weight` | `int` | **Yes** | Number of verified synaptic contacts (T-bars to PSDs). | `48` |
| `roi` | `str` | No | Specific brain or VNC region where synapses occur. | `LO` (Lobula), `PVLP` |
| `confidence` | `float` | No | Machine prediction or proofreading confidence score. | `0.98` |

### 2.3 Neuropil / Region of Interest (ROI) Schema

Brain and ventral nerve cord anatomical partitions:

| Field | Type | Description |
| :--- | :--- | :--- |
| `roi_name` | `str` | Standardized anatomical acronym (e.g., `EB`, `FB`, `MB_CA`, `VNC`). |
| `mesh_id` | `str` | Associated 3D boundary mesh identifier for spatial visualizer. |
| `subsystem` | `str` | Functional category (`Visual`, `Central Complex`, `Olfactory`, `Motor`). |

---

## 3. Provenance Metadata Record

Every graph retrieval query executed by the system logs a `ProvenanceRecord`:

```json
{
  "provenance_id": "prov_cns_20260913_001",
  "dataset_name": "cns",
  "dataset_version": "v1.0",
  "data_provider": "Janelia Research Campus / Google Research",
  "query_endpoint": "https://neuprint.janelia.org/api/custom/custom",
  "query_timestamp": "2026-09-13T00:40:00Z",
  "neuron_ids_queried": ["10005", "10234", "20145"],
  "synaptic_threshold": 5,
  "execution_time_ms": 128.4
}
```
