"""Étage 5 — Découpage du texte normalisé en fragments (chunks)."""

from __future__ import annotations

from typing import List

from scc_ingestion.core.config import ChunkingConfig
from scc_ingestion.core.errors import PipelineError
from scc_ingestion.core.models import Chunk
from scc_ingestion.pipeline.context import IngestionContext
from scc_ingestion.pipeline.stage import Stage


def split_text(text: str, cfg: ChunkingConfig) -> List[str]:
    """Découpe ``text`` en tranches de ``max_chars`` avec recouvrement ``overlap``."""
    if not text:
        return []
    max_chars = max(1, cfg.max_chars)
    overlap = min(max(0, cfg.overlap), max_chars - 1)
    step = max(1, max_chars - overlap)

    if len(text) <= max_chars:
        return [text] if len(text) >= cfg.min_chars else []

    pieces: List[str] = []
    start = 0
    length = len(text)
    while start < length:
        piece = text[start : start + max_chars]
        if len(piece) >= cfg.min_chars:
            pieces.append(piece)
        if start + max_chars >= length:
            break
        start += step
    return pieces


class ChunkingStage(Stage):
    """Transforme le texte normalisé en une liste ordonnée de :class:`Chunk`."""

    name = "découpage"

    def run(self, ctx: IngestionContext) -> None:
        if ctx.normalized_text is None:
            raise PipelineError("Aucun texte normalisé à découper")
        if ctx.document is None:
            raise PipelineError("Document manquant pour le découpage")

        pieces = split_text(ctx.normalized_text, ctx.config.chunking)
        ctx.chunks = [
            Chunk(
                text=piece,
                index=i,
                document_id=ctx.document.id,
                metadata={"source": ctx.source_item.source},
            )
            for i, piece in enumerate(pieces)
        ]
        self._ok(ctx, f"{len(ctx.chunks)} fragment(s)")


__all__ = ["ChunkingStage", "split_text"]
