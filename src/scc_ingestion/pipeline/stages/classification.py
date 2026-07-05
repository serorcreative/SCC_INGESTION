"""Étage 6 — Classification générique (catégorie + tags).

La classification V1 est déterministe et pilotée par la configuration : aucune
règle en dur propre à une source. ``classification_rules`` associe un tag à une
liste de mots-clés recherchés dans le texte normalisé.
"""

from __future__ import annotations

from typing import Dict, List

from scc_ingestion.core.models import Classification, MediaType
from scc_ingestion.pipeline.context import IngestionContext
from scc_ingestion.pipeline.stage import Stage


def classify(
    text: str,
    source: str,
    category: str,
    media_type: MediaType,
    rules: Dict[str, List[str]],
) -> Classification:
    """Produit une :class:`Classification` à partir de règles par mots-clés."""
    haystack = text.lower()
    tags: List[str] = [source, media_type.value]
    for tag, keywords in rules.items():
        if any(kw.lower() in haystack for kw in keywords):
            tags.append(tag)

    # Dédoublonnage en conservant l'ordre.
    seen = set()
    unique_tags = [t for t in tags if not (t in seen or seen.add(t))]

    confidence = 0.9 if text else 0.5  # référence binaire = confiance moindre
    return Classification(
        category=category,
        tags=unique_tags,
        confidence=confidence,
        metadata={"rule_hits": len(unique_tags) - 2},
    )


class ClassificationStage(Stage):
    """Étiquette le document via le connecteur d'origine et les règles de config."""

    name = "classification"

    def run(self, ctx: IngestionContext) -> None:
        # La catégorie par défaut vient du connecteur (métadonnée), sinon du média.
        category = ctx.source_item.metadata.get("category")
        if not category:
            category = ctx.source_item.media_type.value

        text = ctx.normalized_text or ""
        ctx.classification = classify(
            text=text,
            source=ctx.source_item.source,
            category=category,
            media_type=ctx.source_item.media_type,
            rules=ctx.config.classification_rules,
        )
        self._ok(
            ctx,
            f"catégorie « {ctx.classification.category} », "
            f"{len(ctx.classification.tags)} tag(s)",
        )


__all__ = ["ClassificationStage", "classify"]
