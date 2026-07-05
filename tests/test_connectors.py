"""Tests des connecteurs et du registre."""

from __future__ import annotations

from pathlib import Path

import pytest

from scc_ingestion.connectors.base import FileSystemConnector
from scc_ingestion.connectors.registry import BUILTIN_CONNECTORS, ConnectorRegistry
from scc_ingestion.core.errors import ConnectorError
from scc_ingestion.core.models import MediaType

EXPECTED = {
    "chatgpt", "claude", "github", "supabase", "base44", "documents",
    "pdf", "markdown", "images", "audio", "video", "emails",
}


def test_all_expected_connectors_registered():
    registry = ConnectorRegistry()
    assert EXPECTED.issubset(set(registry.available()))


def test_every_connector_respects_interface():
    for cls in BUILTIN_CONNECTORS:
        conn = cls()
        desc = conn.describe()
        assert desc["name"] == cls.name
        assert hasattr(conn, "discover")
        assert hasattr(conn, "fetch")


def test_markdown_connector_discovers_and_fetches(tmp_path: Path):
    (tmp_path / "a.md").write_text("# hi", encoding="utf-8")
    (tmp_path / "b.txt").write_text("ignore", encoding="utf-8")
    registry = ConnectorRegistry()
    conn = registry.get("markdown")
    items = list(conn.discover(tmp_path))
    assert len(items) == 1
    assert items[0].media_type is MediaType.MARKDOWN
    assert items[0].metadata["category"] == "document"
    assert conn.fetch(items[0]) == b"# hi"


def test_supports_filtering():
    registry = ConnectorRegistry()
    pdf = registry.get("pdf")
    assert pdf.supports("x.pdf")
    assert not pdf.supports("x.png")


def test_generic_connector_supports_everything():
    registry = ConnectorRegistry()
    github = registry.get("github")  # extensions vide
    assert github.supports("anything.xyz")


def test_registry_for_path_autodetect():
    registry = ConnectorRegistry()
    conn = registry.for_path("photo.png")
    assert conn is not None
    assert conn.name == "images"


def test_registry_unknown_connector_raises():
    registry = ConnectorRegistry()
    with pytest.raises(ConnectorError):
        registry.get("inexistant")


def test_discover_missing_source_raises():
    conn = ConnectorRegistry().get("markdown")
    with pytest.raises(ConnectorError):
        list(conn.discover("/chemin/qui/nexiste/pas"))


def test_custom_connector_registration():
    class Custom(FileSystemConnector):
        name = "custom"
        category = "test"

    registry = ConnectorRegistry()
    registry.register(Custom)
    assert registry.has("custom")
    assert isinstance(registry.get("custom"), Custom)
