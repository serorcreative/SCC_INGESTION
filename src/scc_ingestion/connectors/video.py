"""Connecteur Vidéo — fichiers vidéo (métadonnées en V1)."""

from __future__ import annotations

from scc_ingestion.connectors.base import FileSystemConnector
from scc_ingestion.core.models import MediaType


class VideoConnector(FileSystemConnector):
    name = "video"
    category = "media"
    media_types = (MediaType.VIDEO,)
    extensions = (".mp4", ".mov", ".mkv", ".avi", ".webm")


__all__ = ["VideoConnector"]
