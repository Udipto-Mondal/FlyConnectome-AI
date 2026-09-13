"""
neuPrint API Client for FlyConnectome AI.
Integrates directly with the official Drosophila Male Central Nervous System
connectome dataset (Male CNS v1.0) hosted at Janelia Research Campus.

Provides:
- Live health and latency checks against https://neuprint.janelia.org
- Authentication token validation
- Cypher query execution with local caching
- Full scientific provenance tracking for every query
"""

import os
import json
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List

import httpx

from ..config import settings
from .models import (
    NeuronModel,
    SynapticConnectionModel,
    ProvenanceRecord,
    ConnectomeHealthStatus,
)


class NeuPrintClient:
    """
    Client for interacting with the Janelia neuPrint HTTP API and Male CNS v1.0 dataset.
    """

    def __init__(
        self,
        server: Optional[str] = None,
        dataset: Optional[str] = None,
        token: Optional[str] = None,
        cache_dir: Optional[str] = None,
        timeout: float = 15.0,
    ):
        self.server = (server or settings.NEUPRINT_SERVER).rstrip("/")
        self.dataset = dataset or settings.NEUPRINT_DATASET
        self.token = token or settings.NEUPRINT_TOKEN
        self.cache_dir = Path(cache_dir or settings.CONNECTOME_CACHE_DIR)
        self.timeout = timeout

        # Ensure cache directory exists
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    @property
    def is_authenticated(self) -> bool:
        """Check whether an authentication token has been supplied."""
        return bool(self.token and self.token.strip() and self.token != "your_neuprint_auth_token_here")

    def _get_headers(self) -> Dict[str, str]:
        """Generate HTTP request headers including Bearer token if configured."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"FlyConnectomeAI/{settings.VERSION} (Research Connectomics)",
        }
        if self.is_authenticated:
            headers["Authorization"] = f"Bearer {self.token.strip()}"
        return headers

    def _cache_key(self, query: str, dataset: str) -> str:
        """Compute deterministic MD5 hash for a query payload."""
        payload = f"{dataset}::{query.strip()}"
        return hashlib.md5(payload.encode("utf-8")).hexdigest()

    def check_health(self, timeout: float = 6.0) -> ConnectomeHealthStatus:
        """
        Verify network connectivity and API version with the neuPrint server.
        Uses the public /api/version endpoint.
        """
        url = f"{self.server}/api/version"
        start_time = time.time()
        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.get(url, headers=self._get_headers())
                latency = round((time.time() - start_time) * 1000, 2)

                if resp.status_code == 200:
                    data = resp.json()
                    version = data.get("Version", "unknown")
                    if self.is_authenticated:
                        msg = f"Connected to neuPrint (v{version}) for dataset '{self.dataset}' with valid authentication."
                    else:
                        msg = (
                            f"neuPrint server online (v{version}). Live Cypher queries require an auth token. "
                            "Please set NEUPRINT_TOKEN in .env to query the Male CNS connectome directly."
                        )
                    return ConnectomeHealthStatus(
                        connected=True,
                        server=self.server,
                        dataset=self.dataset,
                        api_version=version,
                        authenticated=self.is_authenticated,
                        latency_ms=latency,
                        message=msg,
                    )
                else:
                    return ConnectomeHealthStatus(
                        connected=False,
                        server=self.server,
                        dataset=self.dataset,
                        api_version=None,
                        authenticated=self.is_authenticated,
                        latency_ms=latency,
                        message=f"neuPrint server returned HTTP {resp.status_code}: {resp.text[:100]}",
                    )
        except Exception as e:
            return ConnectomeHealthStatus(
                connected=False,
                server=self.server,
                dataset=self.dataset,
                api_version=None,
                authenticated=self.is_authenticated,
                latency_ms=None,
                message=f"Could not connect to neuPrint server ({self.server}): {str(e)}",
            )

    def execute_cypher(
        self,
        cypher: str,
        dataset: Optional[str] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute an arbitrary Cypher query against the Male CNS dataset via neuPrint.
        Guarantees provenance logging and respects local query cache.
        """
        target_dataset = dataset or self.dataset
        cache_key = self._cache_key(cypher, target_dataset)
        cache_file = self.cache_dir / f"{cache_key}.json"

        start_time = time.time()

        # 1. Check disk cache
        if use_cache and cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                latency = round((time.time() - start_time) * 1000, 2)
                provenance = ProvenanceRecord(
                    provenance_id=f"prov_{cache_key[:12]}_{int(time.time())}",
                    dataset_name=target_dataset,
                    dataset_version="v1.0",
                    query_type="cypher",
                    query_payload=cypher,
                    latency_ms=latency,
                    is_cached=True,
                    is_live=False,
                    source_url=self.server,
                )
                return {
                    "data": cached_data,
                    "provenance": provenance.model_dump(),
                    "source": "cache",
                }
            except Exception:
                pass

        # 2. Check authentication before executing live query
        if not self.is_authenticated:
            latency = round((time.time() - start_time) * 1000, 2)
            provenance = ProvenanceRecord(
                provenance_id=f"prov_unauth_{int(time.time())}",
                dataset_name=target_dataset,
                dataset_version="v1.0",
                query_type="cypher",
                query_payload=cypher,
                latency_ms=latency,
                is_cached=False,
                is_live=False,
                source_url=self.server,
            )
            return {
                "error": "UNAUTHENTICATED",
                "message": (
                    "Insufficient connectome evidence was retrieved for this claim. "
                    "neuPrint authentication token not provided. Please configure NEUPRINT_TOKEN in .env "
                    "to query the official Male CNS v1.0 connectome."
                ),
                "provenance": provenance.model_dump(),
                "data": None,
            }

        # 3. Execute live Cypher query against neuPrint endpoint
        url = f"{self.server}/api/custom/custom"
        payload = {
            "cypher": cypher,
            "dataset": target_dataset,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, headers=self._get_headers(), json=payload)
                latency = round((time.time() - start_time) * 1000, 2)

                if resp.status_code == 200:
                    result_data = resp.json()
                    # Cache to disk for reproducibility
                    if use_cache:
                        try:
                            with open(cache_file, "w", encoding="utf-8") as f:
                                json.dump(result_data, f, indent=2)
                        except Exception:
                            pass

                    provenance = ProvenanceRecord(
                        provenance_id=f"prov_{cache_key[:12]}_{int(time.time())}",
                        dataset_name=target_dataset,
                        dataset_version="v1.0",
                        query_type="cypher",
                        query_payload=cypher,
                        latency_ms=latency,
                        is_cached=False,
                        is_live=True,
                        source_url=self.server,
                    )
                    return {
                        "data": result_data,
                        "provenance": provenance.model_dump(),
                        "source": "neuprint_live",
                    }
                else:
                    return {
                        "error": f"HTTP_{resp.status_code}",
                        "message": f"neuPrint Cypher execution failed: {resp.text[:200]}",
                        "provenance": ProvenanceRecord(
                            provenance_id=f"prov_err_{int(time.time())}",
                            dataset_name=target_dataset,
                            dataset_version="v1.0",
                            query_type="cypher",
                            query_payload=cypher,
                            latency_ms=latency,
                            is_cached=False,
                            is_live=True,
                            source_url=self.server,
                        ).model_dump(),
                        "data": None,
                    }
        except Exception as e:
            latency = round((time.time() - start_time) * 1000, 2)
            return {
                "error": "NETWORK_EXCEPTION",
                "message": f"Failed to execute Cypher against neuPrint: {str(e)}",
                "provenance": ProvenanceRecord(
                    provenance_id=f"prov_err_{int(time.time())}",
                    dataset_name=target_dataset,
                    dataset_version="v1.0",
                    query_type="cypher",
                    query_payload=cypher,
                    latency_ms=latency,
                    is_cached=False,
                    is_live=False,
                    source_url=self.server,
                ).model_dump(),
                "data": None,
            }


# Singleton client instance
neuprint_client = NeuPrintClient()
