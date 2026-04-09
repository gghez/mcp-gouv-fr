"""Async HTTP calls to INSEE API Sirene (3.11) on api.insee.fr."""

from __future__ import annotations

import re
from typing import Any

import httpx

_SIREN_RE = re.compile(r"^\d{9}$")
_SIRET_RE = re.compile(r"^\d{14}$")


def normalize_siren(value: str) -> str:
    """Return a 9-digit SIREN string or raise ValueError."""
    digits = "".join(c for c in value.strip() if c.isdigit())
    if not _SIREN_RE.fullmatch(digits):
        raise ValueError("SIREN must be exactly 9 digits (spaces allowed).")
    return digits


def normalize_siret(value: str) -> str:
    """Return a 14-digit SIRET string or raise ValueError."""
    digits = "".join(c for c in value.strip() if c.isdigit())
    if not _SIRET_RE.fullmatch(digits):
        raise ValueError("SIRET must be exactly 14 digits (spaces allowed).")
    return digits


async def get_unite_legale(client: httpx.AsyncClient, siren: str) -> dict[str, Any]:
    """Fetch one unité légale by SIREN as raw JSON."""
    path_siren = normalize_siren(siren)
    response = await client.get(f"siren/{path_siren}")
    response.raise_for_status()
    return response.json()


async def get_etablissement(client: httpx.AsyncClient, siret: str) -> dict[str, Any]:
    """Fetch one établissement by SIRET as raw JSON."""
    path_siret = normalize_siret(siret)
    response = await client.get(f"siret/{path_siret}")
    response.raise_for_status()
    return response.json()
