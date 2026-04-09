"""data.gouv.fr-specific settings."""

from __future__ import annotations

import logging
import os

_log = logging.getLogger(__name__)

DATAGOUV_API_BASE = os.environ.get(
    "MCP_GOUV_DATAGOUV_API_BASE",
    "https://www.data.gouv.fr/api/1",
)

_log.info("datagouv config: DATAGOUV_API_BASE=%s", DATAGOUV_API_BASE)
