"""Pydantic models for data.gouv.fr tool outputs (API v1).

These shapes mirror the public data.gouv API where noted. Field descriptions are
exposed to clients via JSON Schema so agents can interpret results without ad hoc
knowledge of the portal.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

_log = logging.getLogger(__name__)


class OrganizationRef(BaseModel):
    """Publishing organization for a dataset (subset of the API organization object)."""

    model_config = ConfigDict(extra="ignore")

    id: str | None = Field(default=None, description="Organization UUID on data.gouv.fr.")
    name: str | None = Field(default=None, description="Human-readable organization title.")
    slug: str | None = Field(
        default=None,
        description="URL slug for the organization page on data.gouv.fr.",
    )


class ResourceRef(BaseModel):
    """Single downloadable or API resource linked to a dataset (file, API endpoint, etc.)."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str | None = Field(default=None, description="Resource UUID on data.gouv.fr.")
    title: str | None = Field(default=None, description="Label shown for this resource.")
    url: str | None = Field(
        default=None,
        description="Direct URL to download or access the resource when provided by the API.",
    )
    file_format: str | None = Field(
        default=None,
        alias="format",
        description="Format hint from the API (e.g. csv, json, shp); wire key is often 'format'.",
    )
    description: str | None = Field(
        default=None,
        description="Optional resource description from the portal.",
    )
    mime: str | None = Field(
        default=None,
        description="MIME type when the API exposes it (e.g. text/csv).",
    )


class DatasetSummary(BaseModel):
    """One dataset entry as returned inside a search/list response (reduced fields)."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(description="Dataset UUID on data.gouv.fr.")
    title: str = Field(default="", description="Dataset title.")
    slug: str | None = Field(
        default=None,
        description="Stable slug used in portal URLs and accepted by the detail endpoint.",
    )
    description: str | None = Field(
        default=None,
        description="Markdown or plain-text description snippet from the portal.",
    )
    organization: OrganizationRef | None = Field(
        default=None,
        description="Publishing organization metadata when present on the search hit.",
    )


class DatasetSearchOutput(BaseModel):
    """Paginated dataset search results for the ``search_datasets`` tool."""

    model_config = ConfigDict(extra="ignore")

    page: int = Field(default=1, description="Current 1-based page index returned by the API.")
    page_size: int = Field(
        default=20,
        description="Number of items requested per page (may cap server-side).",
    )
    total: int | None = Field(
        default=None,
        description="Total matching datasets reported by the API, if available.",
    )
    next_page: str | None = Field(
        default=None,
        description="Absolute URL to fetch the next page, or null when there is no next page.",
    )
    datasets: list[DatasetSummary] = Field(
        default_factory=list,
        description="Datasets matching the query for this page (API key 'data' mapped here).",
    )

    @classmethod
    def from_api_payload(cls, raw: dict[str, Any]) -> DatasetSearchOutput:
        raw_list = raw.get("data")
        if raw_list is not None and not isinstance(raw_list, list):
            _log.warning(
                "DatasetSearchOutput.from_api_payload: expected list in 'data', got %s",
                type(raw_list).__name__,
            )
        rows: list[Any] = raw_list if isinstance(raw_list, list) else []
        datasets: list[DatasetSummary] = []
        for item in rows:
            if not isinstance(item, dict):
                _log.warning(
                    "DatasetSearchOutput.from_api_payload: skipping non-dict row type=%s",
                    type(item).__name__,
                )
                continue
            try:
                datasets.append(DatasetSummary.model_validate(item))
            except ValidationError as e:
                _log.warning(
                    "DatasetSearchOutput.from_api_payload: skipping invalid dataset row: %s",
                    e,
                )
                continue
        total = raw.get("total")
        return cls(
            page=int(raw.get("page", 1)),
            page_size=int(raw.get("page_size", 20)),
            total=int(total) if total is not None else None,
            next_page=str(raw["next_page"]) if raw.get("next_page") else None,
            datasets=datasets,
        )


class DatasetDetailOutput(BaseModel):
    """Full dataset metadata and resource list for the ``get_dataset`` tool."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(description="Dataset UUID.")
    title: str = Field(default="", description="Dataset title.")
    slug: str | None = Field(
        default=None,
        description="URL slug; can be used as dataset identifier.",
    )
    description: str | None = Field(
        default=None,
        description="Longer dataset description from the portal.",
    )
    license: str | None = Field(
        default=None,
        description="License identifier or title as returned by the API (e.g. ODbL, fr-lo).",
    )
    frequency: str | None = Field(
        default=None,
        description="Update frequency label when provided (e.g. annual, quarterly).",
    )
    temporal_coverage: dict[str, Any] | str | None = Field(
        default=None,
        description="Temporal coverage object or string from the API, if any.",
    )
    organization: OrganizationRef | None = Field(
        default=None,
        description="Organization that publishes this dataset.",
    )
    resources: list[ResourceRef] = Field(
        default_factory=list,
        description="Files and API endpoints attached to the dataset; use URLs to fetch data.",
    )

    @classmethod
    def from_api_payload(cls, raw: dict[str, Any]) -> DatasetDetailOutput:
        payload = {k: v for k, v in raw.items() if k != "resources"}
        res = raw.get("resources")
        resources: list[ResourceRef] = []
        if res is not None and not isinstance(res, list):
            _log.warning(
                "DatasetDetailOutput.from_api_payload: expected list in 'resources', got %s",
                type(res).__name__,
            )
        if isinstance(res, list):
            for r in res:
                if isinstance(r, dict):
                    try:
                        resources.append(ResourceRef.model_validate(r))
                    except ValidationError as e:
                        _log.warning(
                            "DatasetDetailOutput.from_api_payload: skipping invalid resource: %s",
                            e,
                        )
                        continue
                else:
                    _log.warning(
                        "DatasetDetailOutput.from_api_payload: skipping non-dict resource type=%s",
                        type(r).__name__,
                    )
        payload["resources"] = resources
        try:
            return cls.model_validate(payload)
        except ValidationError as e:
            _log.error(
                "DatasetDetailOutput.from_api_payload: payload failed validation: %s keys=%s",
                e,
                list(payload.keys()),
            )
            raise
