"""Unit tests for Radio France GraphQL output models."""

from __future__ import annotations

from mcp_gouv_fr.apis.radiofrance.models import GraphQLExecuteOutput


def test_from_api_payload_data_and_errors() -> None:
    raw = {
        "data": {"grid": {"edges": []}},
        "errors": [
            {
                "message": "Unknown field",
                "locations": [{"line": 1, "column": 5}],
                "path": ["grid", "missing"],
            }
        ],
    }
    out = GraphQLExecuteOutput.from_api_payload(raw)
    assert out.data == {"grid": {"edges": []}}
    assert len(out.errors) == 1
    assert out.errors[0].message == "Unknown field"
    assert out.errors[0].locations is not None
    assert out.errors[0].locations[0].line == 1
    assert out.errors[0].path == ["grid", "missing"]


def test_from_api_payload_data_only() -> None:
    out = GraphQLExecuteOutput.from_api_payload({"data": {"ok": True}})
    assert out.data == {"ok": True}
    assert out.errors == []
