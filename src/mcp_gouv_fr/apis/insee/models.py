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
