"""Tests de l'interface en ligne de commande."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scc_ingestion import __version__
from scc_ingestion.cli import main


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    """Fichier de configuration JSON isolé (chemins absolus sous tmp_path)."""
    cfg = {
        "paths": {
            "raw_sources_root": str(tmp_path / "raw"),
            "work_root": str(tmp_path / "queue"),
            "reports_dir": str(tmp_path / "reports"),
            "logs_dir": str(tmp_path / "logs"),
            "archive_dir": str(tmp_path / "queue" / "_archive"),
            "index_path": str(tmp_path / "queue" / "index.jsonl"),
        },
        "chunking": {"max_chars": 100, "overlap": 10},
        "classification_rules": {"facturation": ["facture"]},
    }
    path = tmp_path / "cfg.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return path


def test_version(capsys):
    assert main(["version"]) == 0
    assert __version__ in capsys.readouterr().out


def test_connectors_lists_all(capsys):
    assert main(["connectors"]) == 0
    out = capsys.readouterr().out
    for name in ["chatgpt", "claude", "github", "pdf", "emails"]:
        assert name in out


def test_doctor(config_file: Path, capsys):
    assert main(["doctor", "--config", str(config_file)]) == 0
    assert "Moteur d'ingestion SCC" in capsys.readouterr().out


def test_ingest_file(tmp_path: Path, config_file: Path, capsys):
    doc = tmp_path / "note.md"
    doc.write_text("# facture\n\ncontenu", encoding="utf-8")
    code = main(["ingest", str(doc), "--source", "markdown", "--config", str(config_file)])
    assert code == 0
    out = capsys.readouterr().out
    assert "OK" in out
    assert (tmp_path / "queue" / "index.jsonl").exists()


def test_watch(tmp_path: Path, capsys):
    root = tmp_path / "raw"
    root.mkdir()
    (root / "new.txt").write_text("x", encoding="utf-8")
    code = main(["watch", str(root), "--dry-run"])
    assert code == 0
    assert "nouveauté" in capsys.readouterr().out.lower()
