"""Pydantic models for Radio France Open API (GraphQL) tool outputs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class GraphQLLocation(BaseModel):
    """Source location for a GraphQL error (when the API provides it)."""

    model_config = ConfigDict(extra="ignore")

    line: int | None = Field(default=None, description="1-based line number in the query.")
    column: int | None = Field(default=None, description="1-based column in the query.")


class GraphQLErrorItem(BaseModel):
    """One GraphQL error object from the ``errors`` array."""

    model_config = ConfigDict(extra="ignore")

    message: str = Field(description="Human-readable error message from the API.")
    locations: list[GraphQLLocation] | None = Field(
        default=None,
        description="Optional list of locations tied to this error.",
    )
    path: list[str | int] | None = Field(
        default=None,
        description="Response path where the error occurred (field names and list indices).",
    )


class GraphQLExecuteOutput(BaseModel):
    """Result of a GraphQL operation against the Radio France Open API."""

    model_config = ConfigDict(extra="ignore")

    data: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Parsed `data` object from the GraphQL response when present; "
            "shape depends on the submitted query."
        ),
    )
    errors: list[GraphQLErrorItem] = Field(
        default_factory=list,
        description=(
            "GraphQL-level errors (validation, resolver failures). "
            "An empty list means no errors were returned in the payload."
        ),
    )

    @classmethod
    def from_api_payload(cls, raw: dict[str, Any]) -> GraphQLExecuteOutput:
        data = raw.get("data")
        data_dict = data if isinstance(data, dict) else None
        err_list = raw.get("errors")
        errors: list[GraphQLErrorItem] = []
        if isinstance(err_list, list):
            for item in err_list:
                if not isinstance(item, dict):
                    continue
                try:
                    locs = item.get("locations")
                    locations: list[GraphQLLocation] | None = None
                    if isinstance(locs, list):
                        parsed_locs: list[GraphQLLocation] = []
                        for loc in locs:
                            if isinstance(loc, dict):
                                try:
                                    parsed_locs.append(GraphQLLocation.model_validate(loc))
                                except ValidationError:
                                    continue
                        locations = parsed_locs or None
                    path_raw = item.get("path")
                    path: list[str | int] | None = None
                    if isinstance(path_raw, list):
                        path = [p for p in path_raw if isinstance(p, (str, int))]
                        path = path or None
                    errors.append(
                        GraphQLErrorItem(
                            message=str(item.get("message", "")),
                            locations=locations,
                            path=path,
                        )
                    )
                except ValidationError:
                    continue
        return cls(data=data_dict, errors=errors)
