"""data.gouv.fr-specific settings."""

from __future__ import annotations

import os

DATAGOUV_API_BASE = os.environ.get(
    "MCP_GOUV_DATAGOUV_API_BASE",
    "https://www.data.gouv.fr/api/1",
)
