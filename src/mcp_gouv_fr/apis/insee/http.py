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


def normalize_search_query(q: str) -> str:
    """Return a non-empty multicriteria query string or raise ValueError."""
    text = q.strip()
    if not text:
        raise ValueError("Multicriteria query q must be non-empty.")
    return text


def _search_params(
    *,
    q: str,
    nombre: int,
    debut: int,
    tri: str | None,
    date: str | None,
    champs: str | None,
    curseur: str | None,
) -> dict[str, str | int]:
    if not 0 <= nombre <= 200_000:
        raise ValueError("nombre must be between 0 and 200000 (API Sirene 3.11).")
    if not 0 <= debut <= 10_000:
        raise ValueError("debut must be between 0 and 10000 (API Sirene 3.11).")
    params: dict[str, str | int] = {
        "q": normalize_search_query(q),
        "nombre": nombre,
        "debut": debut,
    }
    if tri is not None and tri.strip():
        params["tri"] = tri.strip()
    if date is not None and date.strip():
        params["date"] = date.strip()
    if champs is not None and champs.strip():
        params["champs"] = champs.strip()
    if curseur is not None and curseur.strip():
        params["curseur"] = curseur.strip()
    return params


async def search_unites_legales(
    client: httpx.AsyncClient,
    q: str,
    *,
    nombre: int = 20,
    debut: int = 0,
    tri: str | None = None,
    date: str | None = None,
    champs: str | None = None,
    curseur: str | None = None,
) -> dict[str, Any]:
    """Multicriteria search for legal units (GET ``siren``)."""
    params = _search_params(
        q=q, nombre=nombre, debut=debut, tri=tri, date=date, champs=champs, curseur=curseur
    )
    response = await client.get("siren", params=params)
    response.raise_for_status()
    return response.json()


async def search_etablissements(
    client: httpx.AsyncClient,
    q: str,
    *,
    nombre: int = 20,
    debut: int = 0,
    tri: str | None = None,
    date: str | None = None,
    champs: str | None = None,
    curseur: str | None = None,
) -> dict[str, Any]:
    """Multicriteria search for establishments (GET ``siret``)."""
    params = _search_params(
        q=q, nombre=nombre, debut=debut, tri=tri, date=date, champs=champs, curseur=curseur
    )
    response = await client.get("siret", params=params)
    response.raise_for_status()
    return response.json()
