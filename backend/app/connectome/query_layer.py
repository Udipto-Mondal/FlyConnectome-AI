"""
Connectome Query Layer for FlyConnectome AI.
Provides high-level, type-safe query interfaces over the Drosophila Male CNS (v1.0) connectome.
Handles neuron resolution, upstream/downstream partner extraction, synaptic connectivity lookups,
and ROI spatial filtering with strict provenance tracking and cached canonical fixtures.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from .client import NeuPrintClient, neuprint_client
from .models import (
    NeuronModel,
    SynapticConnectionModel,
    ProvenanceRecord,
)
from ..config import settings


class ConnectomeQueryLayer:
    """
    High-level query layer for the Drosophila Male CNS connectome dataset (v1.0).
    """

    def __init__(self, client: Optional[NeuPrintClient] = None):
        self.client = client or neuprint_client
        self.canonical_cache_path = Path(settings.CONNECTOME_CACHE_DIR) / "canonical_male_cns_circuits.json"
        self._canonical_data: Optional[Dict[str, Any]] = None

    def _load_canonical_data(self) -> Dict[str, Any]:
        """Lazy-load canonical circuit fixtures for offline testing / fallback."""
        if self._canonical_data is None:
            if self.canonical_cache_path.exists():
                try:
                    with open(self.canonical_cache_path, "r", encoding="utf-8") as f:
                        self._canonical_data = json.load(f)
                except Exception:
                    self._canonical_data = {"neurons": [], "connections": []}
            else:
                self._canonical_data = {"neurons": [], "connections": []}
        return self._canonical_data

    def get_neuron(self, body_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve full biological metadata for a specific neuron by body ID."""
        start_time = time.time()

        # 1. If authenticated, query live neuPrint
        if self.client.is_authenticated:
            cypher = f"MATCH (n:Neuron {{bodyId: {body_id}}}) RETURN n"
            res = self.client.execute_cypher(cypher)
            if res.get("data") and res["data"].get("data"):
                raw_node = res["data"]["data"][0][0]
                neuron = NeuronModel(
                    body_id=raw_node.get("bodyId", body_id),
                    instance=raw_node.get("instance"),
                    type=raw_node.get("type"),
                    status=raw_node.get("status"),
                    size=raw_node.get("size"),
                    pre=raw_node.get("pre", 0),
                    post=raw_node.get("post", 0),
                    soma_neuropil=raw_node.get("somaNeuropil"),
                    neurotransmitter=raw_node.get("neurotransmitter"),
                    coords=raw_node.get("coords"),
                )
                return {
                    "neuron": neuron.model_dump(),
                    "provenance": res.get("provenance"),
                    "source": "neuprint_live",
                }

        # 2. Check canonical cache
        canonical = self._load_canonical_data()
        for n in canonical.get("neurons", []):
            if n.get("body_id") == body_id:
                latency = round((time.time() - start_time) * 1000, 2)
                provenance = ProvenanceRecord(
                    provenance_id=f"prov_canon_{body_id}_{int(time.time())}",
                    dataset_name=self.client.dataset,
                    dataset_version="v1.0",
                    query_type="neuron_lookup",
                    query_payload=f"bodyId: {body_id}",
                    latency_ms=latency,
                    is_cached=True,
                    is_live=False,
                    source_url=self.client.server,
                )
                neuron = NeuronModel(**n)
                return {
                    "neuron": neuron.model_dump(),
                    "provenance": provenance.model_dump(),
                    "source": "canonical_cache",
                }

        return None

    def find_neurons(
        self,
        query: Optional[str] = None,
        roi: Optional[str] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Search neurons by cell type, instance name, body ID, or innervated ROI.
        """
        start_time = time.time()
        results: List[NeuronModel] = []
        provenance_source = "canonical_cache"
        is_live = False

        # If authenticated, execute live Cypher
        if self.client.is_authenticated:
            where_clauses = []
            if query:
                q_clean = query.strip().replace("'", "\\'")
                if q_clean.isdigit():
                    where_clauses.append(f"n.bodyId = {int(q_clean)}")
                else:
                    where_clauses.append(f"(n.type =~ '(?i).*{q_clean}.*' OR n.instance =~ '(?i).*{q_clean}.*')")
            if roi:
                where_clauses.append(f"n.roiInfo CONTAINS '{roi}'")

            where_str = " AND ".join(where_clauses) if where_clauses else "1=1"
            cypher = f"MATCH (n:Neuron) WHERE {where_str} RETURN n LIMIT {limit}"
            res = self.client.execute_cypher(cypher)
            if res.get("data") and res["data"].get("data"):
                for row in res["data"]["data"]:
                    raw_node = row[0]
                    results.append(
                        NeuronModel(
                            body_id=raw_node.get("bodyId"),
                            instance=raw_node.get("instance"),
                            type=raw_node.get("type"),
                            status=raw_node.get("status"),
                            size=raw_node.get("size"),
                            pre=raw_node.get("pre", 0),
                            post=raw_node.get("post", 0),
                            soma_neuropil=raw_node.get("somaNeuropil"),
                            neurotransmitter=raw_node.get("neurotransmitter"),
                            coords=raw_node.get("coords"),
                        )
                    )
                provenance_source = "neuprint_live"
                is_live = True

        # Fallback to canonical cache
        if not results:
            canonical = self._load_canonical_data()
            q_lower = query.lower().strip() if query else ""
            roi_upper = roi.upper().strip() if roi else ""

            for n in canonical.get("neurons", []):
                name_match = (
                    not q_lower
                    or q_lower in str(n.get("body_id", "")).lower()
                    or q_lower in n.get("instance", "").lower()
                    or q_lower in n.get("type", "").lower()
                )
                roi_match = (
                    not roi_upper
                    or roi_upper in n.get("soma_neuropil", "").upper()
                )
                if name_match and roi_match:
                    results.append(NeuronModel(**n))
                    if len(results) >= limit:
                        break

        latency = round((time.time() - start_time) * 1000, 2)
        provenance = ProvenanceRecord(
            provenance_id=f"prov_search_{int(time.time())}",
            dataset_name=self.client.dataset,
            dataset_version="v1.0",
            query_type="find_neurons",
            query_payload=f"query='{query}', roi='{roi}', limit={limit}",
            latency_ms=latency,
            is_cached=not is_live,
            is_live=is_live,
            source_url=self.client.server,
        )

        return {
            "neurons": [n.model_dump() for n in results],
            "count": len(results),
            "provenance": provenance.model_dump(),
            "source": provenance_source,
        }

    def get_upstream_partners(
        self,
        body_id: int,
        min_synapses: int = 5,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Find upstream (presynaptic) biological input partners for a neuron.
        """
        start_time = time.time()
        connections: List[SynapticConnectionModel] = []
        is_live = False

        if self.client.is_authenticated:
            cypher = (
                f"MATCH (pre:Neuron)-[c:ConnectsTo]->(post:Neuron {{bodyId: {body_id}}}) "
                f"WHERE c.weight >= {min_synapses} "
                f"RETURN pre.bodyId, c.weight, c.roi ORDER BY c.weight DESC LIMIT {limit}"
            )
            res = self.client.execute_cypher(cypher)
            if res.get("data") and res["data"].get("data"):
                for row in res["data"]["data"]:
                    connections.append(
                        SynapticConnectionModel(
                            pre_body_id=row[0],
                            post_body_id=body_id,
                            weight=row[1],
                            roi=row[2] if len(row) > 2 else None,
                        )
                    )
                is_live = True

        if not connections:
            canonical = self._load_canonical_data()
            for c in canonical.get("connections", []):
                if c.get("post_body_id") == body_id and c.get("weight", 0) >= min_synapses:
                    connections.append(SynapticConnectionModel(**c))
                    if len(connections) >= limit:
                        break

        latency = round((time.time() - start_time) * 1000, 2)
        provenance = ProvenanceRecord(
            provenance_id=f"prov_up_{body_id}_{int(time.time())}",
            dataset_name=self.client.dataset,
            dataset_version="v1.0",
            query_type="upstream_partners",
            query_payload=f"target_body_id={body_id}, min_synapses={min_synapses}",
            latency_ms=latency,
            is_cached=not is_live,
            is_live=is_live,
            source_url=self.client.server,
        )

        return {
            "target_body_id": body_id,
            "connections": [c.model_dump() for c in connections],
            "count": len(connections),
            "provenance": provenance.model_dump(),
        }

    def get_downstream_partners(
        self,
        body_id: int,
        min_synapses: int = 5,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Find downstream (postsynaptic) biological output partners for a neuron.
        """
        start_time = time.time()
        connections: List[SynapticConnectionModel] = []
        is_live = False

        if self.client.is_authenticated:
            cypher = (
                f"MATCH (pre:Neuron {{bodyId: {body_id}}})-[c:ConnectsTo]->(post:Neuron) "
                f"WHERE c.weight >= {min_synapses} "
                f"RETURN post.bodyId, c.weight, c.roi ORDER BY c.weight DESC LIMIT {limit}"
            )
            res = self.client.execute_cypher(cypher)
            if res.get("data") and res["data"].get("data"):
                for row in res["data"]["data"]:
                    connections.append(
                        SynapticConnectionModel(
                            pre_body_id=body_id,
                            post_body_id=row[0],
                            weight=row[1],
                            roi=row[2] if len(row) > 2 else None,
                        )
                    )
                is_live = True

        if not connections:
            canonical = self._load_canonical_data()
            for c in canonical.get("connections", []):
                if c.get("pre_body_id") == body_id and c.get("weight", 0) >= min_synapses:
                    connections.append(SynapticConnectionModel(**c))
                    if len(connections) >= limit:
                        break

        latency = round((time.time() - start_time) * 1000, 2)
        provenance = ProvenanceRecord(
            provenance_id=f"prov_down_{body_id}_{int(time.time())}",
            dataset_name=self.client.dataset,
            dataset_version="v1.0",
            query_type="downstream_partners",
            query_payload=f"source_body_id={body_id}, min_synapses={min_synapses}",
            latency_ms=latency,
            is_cached=not is_live,
            is_live=is_live,
            source_url=self.client.server,
        )

        return {
            "source_body_id": body_id,
            "connections": [c.model_dump() for c in connections],
            "count": len(connections),
            "provenance": provenance.model_dump(),
        }

    def get_connectivity(
        self,
        source_ids: List[int],
        target_ids: List[int],
        min_synapses: int = 1,
    ) -> Dict[str, Any]:
        """
        Query verified direct synaptic connections between a set of source and target neurons.
        """
        start_time = time.time()
        connections: List[SynapticConnectionModel] = []
        is_live = False

        if self.client.is_authenticated and source_ids and target_ids:
            s_str = ",".join(str(i) for i in source_ids)
            t_str = ",".join(str(i) for i in target_ids)
            cypher = (
                f"MATCH (pre:Neuron)-[c:ConnectsTo]->(post:Neuron) "
                f"WHERE pre.bodyId IN [{s_str}] AND post.bodyId IN [{t_str}] AND c.weight >= {min_synapses} "
                f"RETURN pre.bodyId, post.bodyId, c.weight, c.roi ORDER BY c.weight DESC"
            )
            res = self.client.execute_cypher(cypher)
            if res.get("data") and res["data"].get("data"):
                for row in res["data"]["data"]:
                    connections.append(
                        SynapticConnectionModel(
                            pre_body_id=row[0],
                            post_body_id=row[1],
                            weight=row[2],
                            roi=row[3] if len(row) > 3 else None,
                        )
                    )
                is_live = True

        if not connections:
            canonical = self._load_canonical_data()
            s_set = set(source_ids)
            t_set = set(target_ids)
            for c in canonical.get("connections", []):
                if c.get("pre_body_id") in s_set and c.get("post_body_id") in t_set and c.get("weight", 0) >= min_synapses:
                    connections.append(SynapticConnectionModel(**c))

        latency = round((time.time() - start_time) * 1000, 2)
        provenance = ProvenanceRecord(
            provenance_id=f"prov_conn_{int(time.time())}",
            dataset_name=self.client.dataset,
            dataset_version="v1.0",
            query_type="connectivity_between",
            query_payload=f"sources={source_ids}, targets={target_ids}, min_synapses={min_synapses}",
            latency_ms=latency,
            is_cached=not is_live,
            is_live=is_live,
            source_url=self.client.server,
        )

        return {
            "source_ids": source_ids,
            "target_ids": target_ids,
            "connections": [c.model_dump() for c in connections],
            "count": len(connections),
            "provenance": provenance.model_dump(),
        }


# Singleton query layer
query_layer = ConnectomeQueryLayer()
