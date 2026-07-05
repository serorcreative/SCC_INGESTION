"""Tests unitaires des fonctions pures des étages."""

from __future__ import annotations

from scc_ingestion.core.config import ChunkingConfig
from scc_ingestion.core.models import MediaType
from scc_ingestion.pipeline.stages.chunking import split_text
from scc_ingestion.pipeline.stages.classification import classify
from scc_ingestion.pipeline.stages.normalization import normalize_text


def test_normalize_line_endings_and_blanks():
    out = normalize_text("a\r\nb\r\n\n\n\nc   \n")
    assert "\r" not in out
    assert "\n\n\n" not in out
    assert out.startswith("a")


def test_normalize_empty():
    assert normalize_text("") == ""


def test_split_short_text_single_chunk():
    cfg = ChunkingConfig(max_chars=100, overlap=10)
    assert split_text("court", cfg) == ["court"]


def test_split_long_text_with_overlap():
    cfg = ChunkingConfig(max_chars=10, overlap=3, min_chars=1)
    text = "abcdefghijklmnopqrstuvwxyz"
    chunks = split_text(text, cfg)
    assert len(chunks) > 1
    # Reconstruction possible (recouvrement) : chaque caractère est couvert.
    assert "".join(dict.fromkeys("".join(chunks))) == text
    assert all(len(c) <= 10 for c in chunks)


def test_split_empty_returns_nothing():
    assert split_text("", ChunkingConfig()) == []


def test_classify_adds_source_and_media_tags():
    result = classify(
        text="ceci contient une facture",
        source="documents",
        category="document",
        media_type=MediaType.TEXT,
        rules={"facturation": ["facture"]},
    )
    assert "documents" in result.tags
    assert "text" in result.tags
    assert "facturation" in result.tags
    assert result.category == "document"


def test_classify_no_keyword_match():
    result = classify(
        text="rien de particulier",
        source="markdown",
        category="document",
        media_type=MediaType.MARKDOWN,
        rules={"facturation": ["facture"]},
    )
    assert "facturation" not in result.tags
    # Source « markdown » + média « markdown » → un seul tag après dédoublonnage.
    assert result.tags == ["markdown"]
