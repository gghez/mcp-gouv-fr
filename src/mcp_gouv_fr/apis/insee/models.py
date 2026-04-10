"""Pydantic models for INSEE Sirene tool outputs (API 3.11).

Field descriptions are exposed to MCP clients as JSON Schema. Nested business
fields follow the upstream API (camelCase keys inside the main object).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class UniteLegaleOutput(BaseModel):
    """Response body for a single SIREN lookup on API Sirene 3.11."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    unite_legale: dict[str, Any] = Field(
        ...,
        alias="uniteLegale",
        description=(
            "Full legal unit (unité légale) object as returned by INSEE; structure matches "
            "official Sirene 3.11 documentation (nested camelCase fields)."
        ),
    )

    @classmethod
    def from_api_payload(cls, raw: dict[str, Any]) -> UniteLegaleOutput:
        return cls.model_validate(raw)


class EtablissementOutput(BaseModel):
    """Response body for a single SIRET lookup on API Sirene 3.11."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    etablissement: dict[str, Any] = Field(
        ...,
        description=(
            "Full establishment (établissement) object as returned by INSEE; structure matches "
            "official Sirene 3.11 documentation (nested camelCase fields)."
        ),
    )

    @classmethod
    def from_api_payload(cls, raw: dict[str, Any]) -> EtablissementOutput:
        return cls.model_validate(raw)


class UnitesLegalesSearchOutput(BaseModel):
    """Response body for multicriteria legal-unit search (GET ``/siren``)."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    header: dict[str, Any] = Field(
        ...,
        description="Paging and status metadata returned by INSEE (total, debut, nombre, …).",
    )
    unites_legales: list[dict[str, Any]] = Field(
        ...,
        alias="unitesLegales",
        description="Legal units matching the query; each item follows the Sirene 3.11 schema.",
    )
    facettes: list[dict[str, Any]] | None = Field(
        default=None,
        alias="facettes",
        description="Optional facet counts when facette.champ was requested.",
    )

    @classmethod
    def from_api_payload(cls, raw: dict[str, Any]) -> UnitesLegalesSearchOutput:
        return cls.model_validate(raw)


class EtablissementsSearchOutput(BaseModel):
    """Response body for multicriteria establishment search (GET ``/siret``)."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    header: dict[str, Any] = Field(
        ...,
        description="Paging and status metadata returned by INSEE (total, debut, nombre, …).",
    )
    etablissements: list[dict[str, Any]] = Field(
        ...,
        description="Establishments matching the query; each item follows the Sirene 3.11 schema.",
    )
    facettes: list[dict[str, Any]] | None = Field(
        default=None,
        alias="facettes",
        description="Optional facet counts when facette.champ was requested.",
    )

    @classmethod
    def from_api_payload(cls, raw: dict[str, Any]) -> EtablissementsSearchOutput:
        return cls.model_validate(raw)
