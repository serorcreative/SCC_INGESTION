"""Tests de la génération de rapports."""

from __future__ import annotations

import json
from pathlib import Path

from scc_ingestion.core.config import IngestionConfig
from scc_ingestion.core.media import detect_media_type
from scc_ingestion.core.models import SourceItem
from scc_ingestion.pipeline.context import IngestionContext
from scc_ingestion.reporting.generator import build_report_payload, write_report


def _context(text_file: Path, config: IngestionConfig) -> IngestionContext:
    item = SourceItem(
        uri=str(text_file),
        source="documents",
        media_type=detect_media_type(text_file),
        metadata={"filename": text_file.name},
    )
    ctx = IngestionContext(source_item=item, config=config)
    ctx.report.add("intégrité", True, "ok")
    ctx.metadata["sha256"] = "abc123"
    return ctx


def test_build_payload_is_json_serializable(text_file: Path, config: IngestionConfig):
    payload = build_report_payload(_context(text_file, config), timestamp="2026-07-05T00:00:00Z")
    dumped = json.dumps(payload)  # ne doit pas lever
    assert '"timestamp": "2026-07-05T00:00:00Z"' in dumped
    assert payload["source"] == "documents"
    assert payload["sha256"] == "abc123"


def test_write_report_creates_json_and_markdown(text_file: Path, config: IngestionConfig):
    ctx = _context(text_file, config)
    paths = write_report(ctx, timestamp="2026-07-05T00:00:00Z")
    assert paths["json"].exists()
    assert paths["markdown"].exists()
    md = paths["markdown"].read_text(encoding="utf-8")
    assert "Rapport d'ingestion" in md
    assert "intégrité" in md
