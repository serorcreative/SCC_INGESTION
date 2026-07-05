"""Tests de bout en bout du pipeline universel."""

from __future__ import annotations

import json
from pathlib import Path

from scc_ingestion.core.config import IngestionConfig
from scc_ingestion.core.media import detect_media_type
from scc_ingestion.core.models import SourceItem
from scc_ingestion.pipeline.context import IngestionContext
from scc_ingestion.pipeline.pipeline import build_default_pipeline


def _run(path: Path, source: str, config: IngestionConfig) -> IngestionContext:
    item = SourceItem(
        uri=str(path),
        source=source,
        media_type=detect_media_type(path),
        metadata={"filename": path.name, "category": source},
    )
    ctx = IngestionContext(source_item=item, config=config)
    return build_default_pipeline().run(ctx)


def test_full_pipeline_text(text_file: Path, config: IngestionConfig):
    ctx = _run(text_file, "documents", config)

    assert ctx.report.ok, ctx.report.to_dict()
    assert not ctx.aborted
    assert ctx.raw_artifact is not None
    assert ctx.raw_artifact.sha256
    assert ctx.document is not None
    assert ctx.normalized_text
    assert len(ctx.chunks) >= 1
    assert ctx.classification is not None
    assert "facturation" in ctx.classification.tags  # mot-clé « facture » présent
    assert len(ctx.cognitive_objects) == 1


def test_pipeline_runs_all_ten_stages(text_file: Path, config: IngestionConfig):
    ctx = _run(text_file, "documents", config)
    labels = [c.label for c in ctx.report.checks]
    for stage_name in [
        "copie RAW", "extraction", "normalisation", "découpage",
        "classification", "objets cognitifs", "indexation", "rapport", "archivage",
    ]:
        assert stage_name in labels


def test_pipeline_writes_index_and_reports(text_file: Path, config: IngestionConfig):
    ctx = _run(text_file, "documents", config)

    # Index JSONL contient l'objet cognitif.
    assert config.index_path.exists()
    lines = config.index_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["id"] == ctx.cognitive_objects[0].id

    # Rapports JSON + Markdown écrits.
    assert Path(ctx.metadata["report_json"]).exists()
    assert Path(ctx.metadata["report_markdown"]).exists()

    # Artefact archivé.
    assert Path(ctx.metadata["archive_path"]).exists()


def test_pipeline_binary_reference(tmp_path: Path, config: IngestionConfig):
    img = tmp_path / "photo.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 20)
    ctx = _run(img, "images", config)

    assert ctx.report.ok
    assert len(ctx.cognitive_objects) == 1
    obj = ctx.cognitive_objects[0]
    assert obj.metadata["reference_only"] is True
    assert len(ctx.chunks) == 0  # aucun texte -> aucun fragment


def test_pipeline_aborts_on_missing_source(tmp_path: Path, config: IngestionConfig):
    ctx = _run(tmp_path / "absent.txt", "documents", config)
    assert ctx.aborted
    assert not ctx.report.ok
    # Les étages suivants sont marqués ignorés mais n'ajoutent pas d'échec.
    assert any("intégrité" in c.label and not c.passed for c in ctx.report.checks)
