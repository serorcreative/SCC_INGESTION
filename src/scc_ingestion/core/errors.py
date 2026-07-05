"""Hiérarchie d'exceptions du moteur d'ingestion.

Toutes les erreurs métier héritent de :class:`IngestionError`, ce qui permet au
pipeline de capturer un échec de manière homogène tout en conservant la cause
précise pour les rapports.
"""

from __future__ import annotations


class IngestionError(Exception):
    """Erreur de base pour toute défaillance du moteur d'ingestion."""


class ConfigError(IngestionError):
    """Configuration absente, illisible ou invalide."""


class ConnectorError(IngestionError):
    """Un connecteur n'a pas pu découvrir ou récupérer une source."""


class IntegrityError(IngestionError):
    """Un contrôle d'intégrité (existence, lisibilité, empreinte) a échoué."""


class DecompressionError(IngestionError):
    """Une archive n'a pas pu être décompressée."""


class ExtractionError(IngestionError):
    """Le contenu exploitable n'a pas pu être extrait de la source."""


class PipelineError(IngestionError):
    """Un étage du pipeline a échoué de manière irrécupérable."""


__all__ = [
    "IngestionError",
    "ConfigError",
    "ConnectorError",
    "IntegrityError",
    "DecompressionError",
    "ExtractionError",
    "PipelineError",
]
