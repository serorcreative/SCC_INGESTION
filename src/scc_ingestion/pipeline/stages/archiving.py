"""Étage 10 — Archivage de la copie RAW traitée.

Range l'artefact brut dans l'archive, classé par source, sous un nom incluant
l'empreinte (déduplication naturelle et traçabilité).
"""

from __future__ import annotations

import shutil

from scc_ingestion.core.errors import PipelineError
from scc_ingestion.pipeline.context import IngestionContext
from scc_ingestion.pipeline.stage import Stage


class ArchivingStage(Stage):
    """Copie l'artefact RAW dans l'archive finale (idempotent par empreinte)."""

    name = "archivage"

    def run(self, ctx: IngestionContext) -> None:
        if ctx.raw_artifact is None:
            raise PipelineError("Aucun artefact RAW à archiver")

        raw = ctx.raw_artifact
        dest_dir = ctx.config.archive_dir / ctx.source_item.source
        dest_dir.mkdir(parents=True, exist_ok=True)

        short_hash = raw.sha256[:12]
        dest = dest_dir / f"{short_hash}_{raw.raw_path.name}"

        if not dest.exists():
            try:
                shutil.copy2(raw.raw_path, dest)
            except OSError as exc:
                raise PipelineError(f"Archivage impossible : {exc}") from exc
            detail = f"archivé → {dest.name}"
        else:
            detail = f"déjà archivé (empreinte {short_hash})"

        ctx.metadata["archive_path"] = str(dest)
        self._ok(ctx, detail)


__all__ = ["ArchivingStage"]
