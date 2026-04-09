"""INSEE / Sirene API settings (credentials from https://portail-api.insee.fr/)."""

from __future__ import annotations

import os

# Base for API Sirene 3.11 (subscribe on the INSEE API portal).
INSEE_SIRENE_API_BASE = os.environ.get(
    "MCP_GOUV_INSEE_SIRENE_API_BASE",
    "https://api.insee.fr/api-sirene/3.11",
)

# Consumer key / integration token from portail-api.insee.fr (header X-INSEE-Api-Key-Integration).
INSEE_API_KEY = os.environ.get("MCP_GOUV_INSEE_API_KEY", "").strip()
