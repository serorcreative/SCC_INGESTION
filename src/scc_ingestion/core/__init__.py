"""Noyau du moteur : modèles, configuration, rapport, erreurs, médias."""

from __future__ import annotations

from scc_ingestion.core.config import IngestionConfig, load_config
from scc_ingestion.core.media import detect_media_type
from scc_ingestion.core.models import (
    Chunk,
    Classification,
    CognitiveObject,
    Document,
    MediaType,
    RawArtifact,
    SourceItem,
    new_id,
)
from scc_ingestion.core.report import Check, Report

__all__ = [
    "IngestionConfig",
    "load_config",
    "detect_media_type",
    "Chunk",
    "Classification",
    "CognitiveObject",
    "Document",
    "MediaType",
    "RawArtifact",
    "SourceItem",
    "new_id",
    "Check",
    "Report",
]
