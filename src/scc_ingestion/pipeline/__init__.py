"""Pipeline universel d'ingestion."""

from __future__ import annotations

from scc_ingestion.pipeline.context import IngestionContext
from scc_ingestion.pipeline.pipeline import Pipeline, build_default_pipeline
from scc_ingestion.pipeline.stage import Stage

__all__ = ["IngestionContext", "Pipeline", "build_default_pipeline", "Stage"]
