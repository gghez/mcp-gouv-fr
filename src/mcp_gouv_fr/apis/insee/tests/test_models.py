"""Unit tests for INSEE Pydantic models."""

from __future__ import annotations

from mcp_gouv_fr.apis.insee.models import (
    EtablissementOutput,
    EtablissementsSearchOutput,
    UniteLegaleOutput,
    UnitesLegalesSearchOutput,
)


def test_unite_legale_from_api_payload() -> None:
    raw = {"uniteLegale": {"siren": "552081317", "sigleUniteLegale": "INSEE"}}
    out = UniteLegaleOutput.from_api_payload(raw)
    assert out.unite_legale["siren"] == "552081317"
    assert out.unite_legale["sigleUniteLegale"] == "INSEE"


def test_etablissement_from_api_payload() -> None:
    raw = {"etablissement": {"siret": "55208131700027", "nic": "00027"}}
    out = EtablissementOutput.from_api_payload(raw)
    assert out.etablissement["siret"] == "55208131700027"


def test_unites_legales_search_from_api_payload() -> None:
    raw = {
        "header": {"total": 1, "debut": 0, "nombre": 20},
        "unitesLegales": [{"siren": "552081317"}],
    }
    out = UnitesLegalesSearchOutput.from_api_payload(raw)
    assert out.header["total"] == 1
    assert out.unites_legales[0]["siren"] == "552081317"
    assert out.facettes is None


def test_etablissements_search_from_api_payload() -> None:
    raw = {
        "header": {"total": 0, "debut": 0, "nombre": 20},
        "etablissements": [],
        "facettes": [],
    }
    out = EtablissementsSearchOutput.from_api_payload(raw)
    assert out.etablissements == []
    assert out.facettes == []
