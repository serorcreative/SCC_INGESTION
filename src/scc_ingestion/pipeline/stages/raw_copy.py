"""Étage 2 — Copie RAW immuable + décompression et inventaire éventuels."""

from __future__ import annotations

import shutil
from pathlib import Path

from scc_ingestion.core.errors import PipelineError
from scc_ingestion.core.models import RawArtifact
from scc_ingestion.pipeline.context import IngestionContext
from scc_ingestion.pipeline.stage import Stage
from scc_ingestion.validators.decompression import decompress, is_archive
from scc_ingestion.validators.hashing import sha256_file


class RawCopyStage(Stage):
    """Copie la source dans l'espace de travail (RAW), sans jamais la modifier."""

    name = "copie RAW"

    def run(self, ctx: IngestionContext) -> None:
        source = Path(ctx.source_item.uri)
        raw_dir = ctx.workdir / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_path = raw_dir / source.name

        try:
            shutil.copy2(source, raw_path)
        except OSError as exc:
            raise PipelineError(f"Copie RAW impossible : {exc}") from exc

        digest = ctx.metadata.get("sha256") or sha256_file(raw_path)
        size = raw_path.stat().st_size

        ctx.raw_artifact = RawArtifact(
            raw_path=raw_path,
            sha256=digest,
            size=size,
            origin_uri=ctx.source_item.uri,
            media_type=ctx.source_item.media_type,
            metadata=dict(ctx.source_item.metadata),
        )

        detail = f"{raw_path.name} ({size} octets)"
        if is_archive(raw_path):
            extracted = decompress(raw_path, ctx.workdir / "extracted")
            ctx.extracted_files = extracted
            ctx.metadata["extracted_count"] = len(extracted)
            detail += f" — archive décompressée : {len(extracted)} fichier(s)"

        self._ok(ctx, detail)


__all__ = ["RawCopyStage"]
