"""
Configuration settings for NeuroGraph AI.
Loads environment variables with structured Pydantic typing and validation.
Supports Phase 0 foundations, Male CNS connectome credentials for Phase 1,
and multi-agent/literature endpoints.
"""

from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import Field

    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
            case_sensitive=False
        )

        # Platform Metadata
        PROJECT_NAME: str = "NeuroGraph AI"
        VERSION: str = "0.3.0"
        PHASE: str = "Phase 2 — Connectome Query Layer"
        ENVIRONMENT: str = "development"
        DEBUG: bool = True
        API_PREFIX: str = "/api"

        # Server Settings
        HOST: str = "0.0.0.0"
        PORT: int = 8000
        CORS_ORIGINS: List[str] = [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://localhost:8000",
            "*"
        ]

        # Connectome Data Source (Phase 1 Integration)
        NEUPRINT_SERVER: str = "https://neuprint.janelia.org"
        NEUPRINT_DATASET: str = "cns"
        NEUPRINT_TOKEN: str = ""
        CONNECTOME_CACHE_DIR: str = "./data/cache/connectome"

        # Agent & LLM Configuration (Phase 5+)
        GEMINI_API_KEY: str = ""
        GEMINI_MODEL: str = "gemini-1.5-pro"
        AGENT_MAX_RETRIES: int = 3
        AGENT_TIMEOUT_SECONDS: int = 60

        # Literature Retrieval (Phase 6)
        EUROPE_PMC_BASE_URL: str = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        PUBMED_EMAIL: str = "researcher@neurograph.ai"

except ImportError:
    from pydantic import BaseModel, Field

    class Settings(BaseModel):
        PROJECT_NAME: str = os.getenv("PROJECT_NAME", "NeuroGraph AI")
        VERSION: str = os.getenv("VERSION", "0.3.0")
        PHASE: str = os.getenv("PHASE", "Phase 2 — Connectome Query Layer")
        ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
        DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
        API_PREFIX: str = os.getenv("API_PREFIX", "/api")

        HOST: str = os.getenv("HOST", "0.0.0.0")
        PORT: int = int(os.getenv("PORT", "8000"))
        CORS_ORIGINS: List[str] = [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://localhost:8000",
            "*"
        ]

        NEUPRINT_SERVER: str = os.getenv("NEUPRINT_SERVER", "https://neuprint.janelia.org")
        NEUPRINT_DATASET: str = os.getenv("NEUPRINT_DATASET", "cns")
        NEUPRINT_TOKEN: str = os.getenv("NEUPRINT_TOKEN", "")
        CONNECTOME_CACHE_DIR: str = os.getenv("CONNECTOME_CACHE_DIR", "./data/cache/connectome")

        GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
        GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
        AGENT_MAX_RETRIES: int = int(os.getenv("AGENT_MAX_RETRIES", "3"))
        AGENT_TIMEOUT_SECONDS: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "60"))

        EUROPE_PMC_BASE_URL: str = os.getenv(
            "EUROPE_PMC_BASE_URL",
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        )
        PUBMED_EMAIL: str = os.getenv("PUBMED_EMAIL", "researcher@neurograph.ai")


settings = Settings()
