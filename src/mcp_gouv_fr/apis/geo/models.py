"""Pydantic models for geo.api.gouv.fr tool outputs.

Shapes follow the public Geo API (Etalab). Field descriptions are exposed to
clients via JSON Schema for agent discovery.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class CodeNom(BaseModel):
    """Minimal administrative entity with a short code and a French label."""

    model_config = ConfigDict(extra="ignore")

    code: str = Field(description="Official INSEE or territorial code as returned by the API.")
    nom: str = Field(description="Human-readable French name (may include accents).")


class CommuneSummary(BaseModel):
    """Commune row from a search/list response or full commune detail."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    nom: str = Field(description="Commune name.")
    code: str = Field(
        description="INSEE municipality code (``code commune``), 5 characters for mainland.",
    )
    codes_postaux: list[str] | None = Field(
        default=None,
        alias="codesPostaux",
        description="Postal codes served by this commune when the API includes them.",
    )
    departement: CodeNom | None = Field(
        default=None,
        description="Parent department when nested in the payload.",
    )
    region: CodeNom | None = Field(
        default=None,
        description="Parent region when nested in the payload.",
    )
    population: int | None = Field(
        default=None,
        description="Population figure when requested via ``fields`` on the detail endpoint.",
    )
    surface: float | None = Field(
        default=None,
        description="Area in hectares when provided by the API.",
    )
    score: float | None = Field(
        default=None,
        alias="_score",
        description="Relevance score for fuzzy name search; absent on exact or non-search calls.",
    )


class CommuneSearchOutput(BaseModel):
    """List of communes returned by ``search_communes``."""

    model_config = ConfigDict(extra="ignore")

    communes: list[CommuneSummary] = Field(
        default_factory=list,
        description=(
            "Matching communes in API order (often best match first when searching by name)."
        ),
    )

    @classmethod
    def from_api_list(cls, raw: list[Any]) -> CommuneSearchOutput:
        items: list[CommuneSummary] = []
        for row in raw:
            if not isinstance(row, dict):
                continue
            try:
                items.append(CommuneSummary.model_validate(row))
            except ValidationError:
                continue
        return cls(communes=items)


class DepartementSummary(BaseModel):
    """Department row from list/search or embedded under a commune."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    nom: str = Field(description="Department name.")
    code: str = Field(description="Official department code (e.g. ``75``, ``2B``).")
    region: CodeNom | None = Field(
        default=None,
        description="Parent region when the API nests it.",
    )
    score: float | None = Field(
        default=None,
        alias="_score",
        description="Relevance score when filtering departments by ``nom``.",
    )


class DepartementSearchOutput(BaseModel):
    """List of departments from ``search_departements``."""

    model_config = ConfigDict(extra="ignore")

    departements: list[DepartementSummary] = Field(
        default_factory=list,
        description="Departments returned for this query (full list when ``nom`` is omitted).",
    )

    @classmethod
    def from_api_list(cls, raw: list[Any]) -> DepartementSearchOutput:
        items: list[DepartementSummary] = []
        for row in raw:
            if not isinstance(row, dict):
                continue
            try:
                items.append(DepartementSummary.model_validate(row))
            except ValidationError:
                continue
        return cls(departements=items)


class RegionSummary(BaseModel):
    """Region row from list/search or nested reference."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    nom: str = Field(description="Region name.")
    code: str = Field(description="Official region code (two digits as string).")
    score: float | None = Field(
        default=None,
        alias="_score",
        description="Relevance score when filtering regions by ``nom``.",
    )


class RegionSearchOutput(BaseModel):
    """List of regions from ``search_regions``."""

    model_config = ConfigDict(extra="ignore")

    regions: list[RegionSummary] = Field(
        default_factory=list,
        description="Regions returned for this query (full list when ``nom`` is omitted).",
    )

    @classmethod
    def from_api_list(cls, raw: list[Any]) -> RegionSearchOutput:
        items: list[RegionSummary] = []
        for row in raw:
            if not isinstance(row, dict):
                continue
            try:
                items.append(RegionSummary.model_validate(row))
            except ValidationError:
                continue
        return cls(regions=items)
