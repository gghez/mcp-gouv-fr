"""Tests for Pydantic tool output models (data.gouv API)."""

from __future__ import annotations

from mcp_gouv_fr.apis.datagouv.models import DatasetDetailOutput, DatasetSearchOutput


def test_dataset_search_from_api_maps_data_to_datasets() -> None:
    raw = {
        "data": [
            {
                "id": "ds1",
                "title": "Tax data",
                "slug": "tax-data",
                "organization": {"id": "o1", "name": "Ministry"},
            }
        ],
        "page": 2,
        "page_size": 10,
        "total": 42,
        "next_page": "https://example.com/next",
    }
    out = DatasetSearchOutput.from_api_payload(raw)
    assert out.page == 2
    assert out.page_size == 10
    assert out.total == 42
    assert out.next_page == "https://example.com/next"
    assert len(out.datasets) == 1
    assert out.datasets[0].id == "ds1"
    assert out.datasets[0].title == "Tax data"
    assert out.datasets[0].organization is not None
    assert out.datasets[0].organization.name == "Ministry"


def test_dataset_search_skips_invalid_rows() -> None:
    raw = {"data": [{"id": "ok", "title": "A"}, {"title": "missing id"}], "page": 1}
    out = DatasetSearchOutput.from_api_payload(raw)
    assert len(out.datasets) == 1
    assert out.datasets[0].id == "ok"


def test_dataset_detail_from_api_parses_resources() -> None:
    raw = {
        "id": "abc",
        "title": "Full dataset",
        "resources": [
            {"id": "r1", "title": "CSV", "url": "https://x/c.csv", "format": "csv"},
        ],
    }
    out = DatasetDetailOutput.from_api_payload(raw)
    assert out.id == "abc"
    assert len(out.resources) == 1
    assert out.resources[0].file_format == "csv"
    assert out.resources[0].url == "https://x/c.csv"
