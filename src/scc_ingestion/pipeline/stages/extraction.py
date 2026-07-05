"""Étage 3 — Extraction du contenu exploitable à partir de la copie RAW."""

from __future__ import annotations

from scc_ingestion.core.errors import ExtractionError
from scc_ingestion.pipeline.context import IngestionContext
from scc_ingestion.pipeline.extractors import get_extractor
from scc_ingestion.pipeline.stage import Stage


class ExtractionStage(Stage):
    """Sélectionne l'extracteur adapté au ``media_type`` et produit un Document."""

    name = "extraction"

    def run(self, ctx: IngestionContext) -> None:
        if ctx.raw_artifact is None:
            raise ExtractionError("Aucun artefact RAW à extraire")

        try:
            data = ctx.raw_artifact.raw_path.read_bytes()
        except OSError as exc:
            raise ExtractionError(f"Lecture RAW impossible : {exc}") from exc

        extractor = get_extractor(ctx.raw_artifact.media_type)
        meta = dict(ctx.raw_artifact.metadata)
        meta["media_type"] = ctx.raw_artifact.media_type.value
        document = extractor(data, meta)
        ctx.document = document

        if document.metadata.get("reference_only"):
            detail = f"actif binaire ({document.media_type.value}) — document de référence"
        else:
            detail = f"{document.length} caractères extraits ({document.media_type.value})"
        self._ok(ctx, detail)


__all__ = ["ExtractionStage"]
