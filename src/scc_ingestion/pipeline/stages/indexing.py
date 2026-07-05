"""Étage 8 — Indexation des objets cognitifs.

Écrit chaque objet dans un index JSONL append-only (traçable, simple à relire)
et dépose une copie JSON par objet dans l'espace de travail de l'exécution.
"""

from __future__ import annotations

import json

from scc_ingestion.core.errors import PipelineError
from scc_ingestion.pipeline.context import IngestionContext
from scc_ingestion.pipeline.stage import Stage


class IndexingStage(Stage):
    """Persiste les objets cognitifs dans l'index global et l'espace de run."""

    name = "indexation"

    def run(self, ctx: IngestionContext) -> None:
        if not ctx.cognitive_objects:
            raise PipelineError("Aucun objet cognitif à indexer")

        index_path = ctx.config.index_path
        index_path.parent.mkdir(parents=True, exist_ok=True)
        objects_dir = ctx.workdir / "objects"
        objects_dir.mkdir(parents=True, exist_ok=True)

        with open(index_path, "a", encoding="utf-8") as index:
            for obj in ctx.cognitive_objects:
                record = obj.to_dict()
                index.write(json.dumps(record, ensure_ascii=False) + "\n")
                (objects_dir / f"{obj.id}.json").write_text(
                    json.dumps(record, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

        ctx.metadata["index_path"] = str(index_path)
        self._ok(ctx, f"{len(ctx.cognitive_objects)} objet(s) indexé(s) → {index_path.name}")


__all__ = ["IndexingStage"]
