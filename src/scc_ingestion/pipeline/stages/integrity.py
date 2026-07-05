"""Étage 1 — Contrôle d'intégrité de la source."""

from __future__ import annotations

from pathlib import Path

from scc_ingestion.core.errors import IntegrityError
from scc_ingestion.pipeline.context import IngestionContext
from scc_ingestion.pipeline.stage import Stage
from scc_ingestion.validators.integrity import check_integrity


class IntegrityStage(Stage):
    """Vérifie existence, lisibilité, non-vacuité et calcule l'empreinte."""

    name = "intégrité"

    def run(self, ctx: IngestionContext) -> None:
        uri = ctx.source_item.uri
        path = Path(uri)
        if not path.exists():
            raise IntegrityError(f"Source locale introuvable : {uri}")

        report, digest = check_integrity(path)
        ctx.report.merge(report)
        if not report.ok or digest is None:
            raise IntegrityError(f"Contrôle d'intégrité échoué pour {uri}")

        ctx.metadata["sha256"] = digest
        ctx.metadata["source_size"] = path.stat().st_size


__all__ = ["IntegrityStage"]
