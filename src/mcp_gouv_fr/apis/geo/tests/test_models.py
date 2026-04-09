"""Tests for Pydantic tool output models (Geo API)."""

from __future__ import annotations

from mcp_gouv_fr.apis.geo.models import (
    CommuneSearchOutput,
    CommuneSummary,
    DepartementSearchOutput,
    RegionSearchOutput,
)


def test_commune_search_from_api_list() -> None:
    raw = [
        {
            "nom": "Paris",
            "code": "75056",
            "codesPostaux": ["75001"],
            "_score": 1.5,
        }
    ]
    out = CommuneSearchOutput.from_api_list(raw)
    assert len(out.communes) == 1
    assert out.communes[0].nom == "Paris"
    assert out.communes[0].score == 1.5


def test_commune_search_skips_invalid_rows() -> None:
    raw = [{"nom": "Ok", "code": "1"}, {"nom": "missing code"}]
    out = CommuneSearchOutput.from_api_list(raw)
    assert len(out.communes) == 1


def test_commune_detail_validate() -> None:
    raw = {
        "nom": "Paris",
        "code": "75056",
        "departement": {"code": "75", "nom": "Paris"},
        "population": 2000000,
    }
    c = CommuneSummary.model_validate(raw)
    assert c.departement is not None
    assert c.departement.code == "75"
    assert c.population == 2000000


def test_departement_search_from_api_list() -> None:
    raw = [{"nom": "Ain", "code": "01", "_score": 0.9}]
    out = DepartementSearchOutput.from_api_list(raw)
    assert len(out.departements) == 1
    assert out.departements[0].score == 0.9


def test_region_search_from_api_list() -> None:
    raw = [{"nom": "Bretagne", "code": "53"}]
    out = RegionSearchOutput.from_api_list(raw)
    assert len(out.regions) == 1
    assert out.regions[0].code == "53"
