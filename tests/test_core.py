"""Tests du noyau : modèles, détection média, rapport, configuration."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scc_ingestion.core.config import load_config
from scc_ingestion.core.errors import ConfigError
from scc_ingestion.core.media import detect_media_type, extensions_for
from scc_ingestion.core.models import (
    CognitiveObject,
    MediaType,
    SourceItem,
    new_id,
)
from scc_ingestion.core.report import Report


def test_new_id_is_unique_and_prefixed():
    a, b = new_id("run"), new_id("run")
    assert a != b
    assert a.startswith("run_")


def test_detect_media_type():
    assert detect_media_type("a.md") is MediaType.MARKDOWN
    assert detect_media_type("a.PDF") is MediaType.PDF
    assert detect_media_type("a.unknownext") is MediaType.UNKNOWN
    assert ".png" in extensions_for(MediaType.IMAGE)


def test_source_item_path(tmp_path: Path):
    f = tmp_path / "x.txt"
    f.write_text("hi", encoding="utf-8")
    item = SourceItem(uri=str(f), source="test", media_type=MediaType.TEXT)
    assert item.path == f
    missing = SourceItem(uri=str(tmp_path / "none.txt"), source="test")
    assert missing.path is None


def test_cognitive_object_to_dict_roundtrip():
    obj = CognitiveObject(title="T", content="C", tags=["a"], category="cat")
    data = obj.to_dict()
    assert data["title"] == "T"
    assert data["tags"] == ["a"]
    assert json.loads(json.dumps(data))["category"] == "cat"


def test_report_ok_and_counts():
    report = Report("r")
    assert report.ok  # rapport vide = ok
    report.add("a", True, "")
    report.add("b", False, "boom")
    assert not report.ok
    assert report.passed_count == 1
    assert report.failed_count == 1
    assert report.to_dict()["failed"] == 1


def test_report_merge():
    r1, r2 = Report("1"), Report("2")
    r1.add("x", True)
    r2.add("y", True)
    r1.merge(r2)
    assert len(r1.checks) == 2


def test_load_config_defaults_without_file():
    cfg = load_config()  # aucun chemin -> défauts, pas d'erreur
    assert cfg.chunking.max_chars > 0
    assert "02_RAW_SOURCES" in str(cfg.raw_sources_root)


def test_load_config_missing_explicit_raises(tmp_path: Path):
    with pytest.raises(ConfigError):
        load_config(tmp_path / "absent.json")


def test_load_config_reads_values(tmp_path: Path):
    cfg_file = tmp_path / "c.json"
    cfg_file.write_text(
        json.dumps(
            {
                "chunking": {"max_chars": 123, "overlap": 7},
                "enabled_sources": ["pdf"],
                "classification_rules": {"t": ["kw"]},
            }
        ),
        encoding="utf-8",
    )
    cfg = load_config(cfg_file)
    assert cfg.chunking.max_chars == 123
    assert cfg.enabled_sources == ["pdf"]
    assert cfg.classification_rules == {"t": ["kw"]}
