"""Unit tests for INSEE Pydantic models."""

from __future__ import annotations

from mcp_gouv_fr.apis.insee.models import EtablissementOutput, UniteLegaleOutput


def test_unite_legale_from_api_payload() -> None:
    raw = {"uniteLegale": {"siren": "552081317", "sigleUniteLegale": "INSEE"}}
    out = UniteLegaleOutput.from_api_payload(raw)
    assert out.unite_legale["siren"] == "552081317"
    assert out.unite_legale["sigleUniteLegale"] == "INSEE"


def test_etablissement_from_api_payload() -> None:
    raw = {"etablissement": {"siret": "55208131700027", "nic": "00027"}}
    out = EtablissementOutput.from_api_payload(raw)
    assert out.etablissement["siret"] == "55208131700027"
