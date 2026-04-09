"""Tests for API registry and key warnings."""

from __future__ import annotations

import logging

import pytest

from mcp_gouv_fr.apis import resolve_api_mounts, warn_if_missing_api_keys

_ALL_API_IDS = ["datagouv", "geo", "insee", "radiofrance"]


def test_resolve_api_mounts_none_loads_all() -> None:
    all_ids = [ns for ns, _ in resolve_api_mounts(None)]
    assert all_ids == _ALL_API_IDS


def test_resolve_api_mounts_empty_loads_all() -> None:
    all_ids = [ns for ns, _ in resolve_api_mounts([])]
    assert all_ids == _ALL_API_IDS


def test_resolve_api_mounts_subset_order() -> None:
    mounts = resolve_api_mounts(["insee", "datagouv", "geo"])
    assert [ns for ns, _ in mounts] == ["insee", "datagouv", "geo"]


def test_resolve_api_mounts_unknown() -> None:
    with pytest.raises(ValueError, match="unknown API"):
        resolve_api_mounts(["typo"])


def test_warn_insee_missing_key_logs(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)
    warn_if_missing_api_keys(["insee"])
    assert any("MCP_GOUV_INSEE_API_KEY" in r.message for r in caplog.records)


def test_warn_skips_datagouv(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)
    warn_if_missing_api_keys(["datagouv"])
    assert caplog.records == []


def test_warn_insee_skipped_when_key_set(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.WARNING)
    monkeypatch.setenv("MCP_GOUV_INSEE_API_KEY", "test-key")
    warn_if_missing_api_keys(["insee"])
    assert not any("MCP_GOUV_INSEE_API_KEY" in r.message for r in caplog.records)


def test_warn_radiofrance_missing_token_logs(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)
    warn_if_missing_api_keys(["radiofrance"])
    assert any("MCP_GOUV_RADIOFRANCE_API_TOKEN" in r.message for r in caplog.records)
