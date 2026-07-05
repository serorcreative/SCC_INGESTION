"""Étage 4 — Normalisation du texte extrait.

Uniformise encodage (NFC), fins de ligne, espaces superflus et lignes vides
consécutives, pour offrir un texte stable au découpage et à l'indexation.
"""

from __future__ import annotations

import re
import unicodedata

from scc_ingestion.core.errors import PipelineError
from scc_ingestion.pipeline.context import IngestionContext
from scc_ingestion.pipeline.stage import Stage

_MULTI_BLANK = re.compile(r"\n{3,}")
_TRAILING_WS = re.compile(r"[ \t]+\n")


def normalize_text(text: str) -> str:
    """Normalise un texte brut de manière déterministe."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.lstrip("﻿")  # BOM éventuel
    text = _TRAILING_WS.sub("\n", text)
    text = _MULTI_BLANK.sub("\n\n", text)
    return text.strip()


class NormalizationStage(Stage):
    """Applique :func:`normalize_text` au contenu du document."""

    name = "normalisation"

    def run(self, ctx: IngestionContext) -> None:
        if ctx.document is None:
            raise PipelineError("Aucun document à normaliser")

        normalized = normalize_text(ctx.document.text)
        ctx.normalized_text = normalized
        self._ok(ctx, f"{len(normalized)} caractères normalisés")


__all__ = ["NormalizationStage", "normalize_text"]
