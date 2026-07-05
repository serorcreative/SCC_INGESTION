"""Étages du pipeline universel, dans l'ordre canonique d'exécution."""

from __future__ import annotations

from scc_ingestion.pipeline.stages.archiving import ArchivingStage
from scc_ingestion.pipeline.stages.chunking import ChunkingStage
from scc_ingestion.pipeline.stages.classification import ClassificationStage
from scc_ingestion.pipeline.stages.cognitive import CognitiveStage
from scc_ingestion.pipeline.stages.extraction import ExtractionStage
from scc_ingestion.pipeline.stages.indexing import IndexingStage
from scc_ingestion.pipeline.stages.integrity import IntegrityStage
from scc_ingestion.pipeline.stages.normalization import NormalizationStage
from scc_ingestion.pipeline.stages.raw_copy import RawCopyStage
from scc_ingestion.pipeline.stages.reporting import ReportingStage

__all__ = [
    "IntegrityStage",
    "RawCopyStage",
    "ExtractionStage",
    "NormalizationStage",
    "ChunkingStage",
    "ClassificationStage",
    "CognitiveStage",
    "IndexingStage",
    "ReportingStage",
    "ArchivingStage",
]
