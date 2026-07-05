"""Orchestrateur du pipeline universel.

Enchaîne des :class:`Stage` sur un :class:`IngestionContext`. La séquence est
identique pour **toutes** les sources — c'est ce qui rend le moteur générique.
Chaque étage est isolé : une exception est capturée, transformée en échec dans
le rapport, et (si ``stop_on_error``) interrompt proprement la suite.
"""

from __future__ import annotations

from typing import List, Optional, Sequence

from scc_ingestion.core.errors import IngestionError
from scc_ingestion.pipeline.context import IngestionContext
from scc_ingestion.pipeline.stage import Stage


class Pipeline:
    """Séquence ordonnée d'étages exécutée sur un contexte."""

    def __init__(self, stages: Sequence[Stage], stop_on_error: bool = True):
        self.stages: List[Stage] = list(stages)
        self.stop_on_error = stop_on_error

    def run(self, ctx: IngestionContext) -> IngestionContext:
        """Exécute tous les étages sur ``ctx`` et retourne le contexte enrichi."""
        for stage in self.stages:
            if ctx.aborted:
                ctx.report.add(stage.name, True, "étage ignoré (exécution interrompue)")
                continue
            try:
                stage.run(ctx)
            except IngestionError as exc:
                ctx.report.add(stage.name, False, str(exc))
                if self.stop_on_error:
                    ctx.abort(f"échec à l'étage « {stage.name} » : {exc}")
            except Exception as exc:  # noqa: BLE001 - filet de sécurité générique
                ctx.report.add(stage.name, False, f"erreur inattendue : {exc}")
                if self.stop_on_error:
                    ctx.abort(f"erreur inattendue à l'étage « {stage.name} » : {exc}")
        return ctx

    def stage_names(self) -> List[str]:
        return [stage.name for stage in self.stages]


def build_default_pipeline(stop_on_error: bool = True) -> Pipeline:
    """Construit le pipeline universel V1 dans l'ordre canonique.

    Source → Intégrité → Copie RAW → Extraction → Normalisation → Découpage →
    Classification → Objets cognitifs → Indexation → Rapport → Archivage.
    """
    # Import local pour éviter tout cycle au chargement du module.
    from scc_ingestion.pipeline.stages import (
        ArchivingStage,
        ChunkingStage,
        ClassificationStage,
        CognitiveStage,
        ExtractionStage,
        IndexingStage,
        IntegrityStage,
        NormalizationStage,
        RawCopyStage,
        ReportingStage,
    )

    stages: List[Stage] = [
        IntegrityStage(),
        RawCopyStage(),
        ExtractionStage(),
        NormalizationStage(),
        ChunkingStage(),
        ClassificationStage(),
        CognitiveStage(),
        IndexingStage(),
        ReportingStage(),
        ArchivingStage(),
    ]
    return Pipeline(stages, stop_on_error=stop_on_error)


__all__ = ["Pipeline", "build_default_pipeline"]
