"""Fixtures partagées : configuration isolée et sources d'exemple."""

from __future__ import annotations

from pathlib import Path

import pytest

from scc_ingestion.core.config import ChunkingConfig, IngestionConfig


@pytest.fixture
def config(tmp_path: Path) -> IngestionConfig:
    """Configuration entièrement isolée dans ``tmp_path`` (aucun effet de bord réel)."""
    cfg = IngestionConfig(
        engine_root=tmp_path,
        raw_sources_root=tmp_path / "raw_sources",
        work_root=tmp_path / "queue",
        reports_dir=tmp_path / "reports",
        logs_dir=tmp_path / "logs",
        archive_dir=tmp_path / "queue" / "_archive",
        index_path=tmp_path / "queue" / "index.jsonl",
        chunking=ChunkingConfig(max_chars=50, overlap=10, min_chars=1),
        classification_rules={"facturation": ["facture", "montant"]},
    )
    cfg.ensure_directories()
    return cfg


@pytest.fixture
def text_file(tmp_path: Path) -> Path:
    """Un fichier texte d'exemple contenant un mot-clé de classification."""
    path = tmp_path / "note.txt"
    path.write_text(
        "Ceci est une facture de test.\nMontant : 100 CHF.\n" * 5,
        encoding="utf-8",
    )
    return path


@pytest.fixture
def markdown_file(tmp_path: Path) -> Path:
    path = tmp_path / "doc.md"
    path.write_text("# Titre\n\nContenu de projet.\n", encoding="utf-8")
    return path
