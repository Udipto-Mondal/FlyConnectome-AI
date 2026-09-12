"""
Phase 0 Automated Tests for NeuroGraph AI Configuration Layer.
"""

import os
import pytest
from app.config import Settings


def test_settings_defaults():
    """Verify default configuration attributes are properly loaded."""
    s = Settings()
    assert s.PROJECT_NAME == "NeuroGraph AI"
    assert "Phase 2" in s.PHASE
    assert s.PORT == 8000
    assert s.DEBUG is True
    assert "cns" in s.NEUPRINT_DATASET.lower()
    assert "https://neuprint.janelia.org" in s.NEUPRINT_SERVER
    assert "europepmc" in s.EUROPE_PMC_BASE_URL.lower()


def test_cors_origins_type():
    """Verify CORS origins is a valid list."""
    s = Settings()
    assert isinstance(s.CORS_ORIGINS, list)
    assert len(s.CORS_ORIGINS) > 0


def test_neuprint_config_fields():
    """Verify neuPrint fields exist for upcoming Phase 1 integration."""
    s = Settings()
    assert hasattr(s, "NEUPRINT_SERVER")
    assert hasattr(s, "NEUPRINT_DATASET")
    assert hasattr(s, "NEUPRINT_TOKEN")
    assert hasattr(s, "CONNECTOME_CACHE_DIR")
