"""Étage 9 — Génération du rapport d'exécution."""

from __future__ import annotations

from scc_ingestion.pipeline.context import IngestionContext
from scc_ingestion.pipeline.stage import Stage
from scc_ingestion.reporting.generator import write_report


class ReportingStage(Stage):
    """Écrit le rapport JSON + Markdown de l'exécution."""

    name = "rapport"

    def run(self, ctx: IngestionContext) -> None:
        paths = write_report(ctx)
        ctx.metadata["report_json"] = str(paths["json"])
        ctx.metadata["report_markdown"] = str(paths["markdown"])
        self._ok(ctx, f"rapport écrit → {paths['json'].name}")


__all__ = ["ReportingStage"]
