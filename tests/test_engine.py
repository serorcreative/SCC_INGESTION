"""Tests de la façade IngestionEngine."""

from __future__ import annotations

from pathlib import Path

import pytest

from scc_ingestion.core.config import IngestionConfig
from scc_ingestion.core.errors import ConnectorError
from scc_ingestion.engine import IngestionEngine


def test_engine_ingest_path_autodetect(markdown_file: Path, config: IngestionConfig):
    engine = IngestionEngine(config=config)
    contexts = engine.ingest_path(markdown_file)  # auto-détection markdown
    assert len(contexts) == 1
    assert contexts[0].report.ok
    assert contexts[0].source_item.source == "markdown"


def test_engine_ingest_directory(tmp_path: Path, config: IngestionConfig):
    d = tmp_path / "exports"
    d.mkdir()
    (d / "a.md").write_text("# a", encoding="utf-8")
    (d / "b.md").write_text("# b", encoding="utf-8")
    engine = IngestionEngine(config=config)
    contexts = engine.ingest_path(d, connector_name="markdown")
    assert len(contexts) == 2
    assert all(c.report.ok for c in contexts)


def test_engine_resolve_connector_unknown_path(tmp_path: Path, config: IngestionConfig):
    engine = IngestionEngine(config=config)
    with pytest.raises(ConnectorError):
        engine.resolve_connector(tmp_path / "mystere.zzz")


def test_engine_ingest_file_as(text_file: Path, config: IngestionConfig):
    engine = IngestionEngine(config=config)
    ctx = engine.ingest_file_as(text_file, source="chatgpt")
    assert ctx.source_item.source == "chatgpt"
    assert ctx.report.ok
