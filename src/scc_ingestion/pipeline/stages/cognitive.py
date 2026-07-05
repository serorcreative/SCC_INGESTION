"""Étage 7 — Création des objets cognitifs.

Assemble document + fragments + classification en un ou plusieurs
:class:`CognitiveObject`, unité de connaissance consommée par les couches
supérieures de SCC. En V1, un objet cognitif est produit par document.
"""

from __future__ import annotations

from scc_ingestion.core.errors import PipelineError
from scc_ingestion.core.models import CognitiveObject
from scc_ingestion.pipeline.context import IngestionContext
from scc_ingestion.pipeline.stage import Stage


class CognitiveStage(Stage):
    """Construit les objets cognitifs de l'exécution."""

    name = "objets cognitifs"

    def run(self, ctx: IngestionContext) -> None:
        if ctx.document is None or ctx.classification is None:
            raise PipelineError("Document ou classification manquant")

        filename = ctx.source_item.metadata.get("filename", ctx.source_item.uri)
        title = ctx.metadata.get("title") or filename

        content = ctx.normalized_text or ""
        if not content:
            # Actif binaire : objet cognitif « catalogue » pointant vers la source.
            content = f"[{ctx.document.media_type.value}] {filename}"

        obj = CognitiveObject(
            title=title,
            content=content,
            category=ctx.classification.category,
            tags=list(ctx.classification.tags),
            source=ctx.source_item.source,
            origin_uri=ctx.source_item.uri,
            checksum=ctx.raw_artifact.sha256 if ctx.raw_artifact else "",
            chunk_ids=[c.id for c in ctx.chunks],
            metadata={
                "run_id": ctx.run_id,
                "media_type": ctx.document.media_type.value,
                "chunk_count": len(ctx.chunks),
                "reference_only": bool(ctx.document.metadata.get("reference_only")),
            },
        )
        ctx.cognitive_objects.append(obj)
        self._ok(ctx, f"{len(ctx.cognitive_objects)} objet(s) cognitif(s)")


__all__ = ["CognitiveStage"]
