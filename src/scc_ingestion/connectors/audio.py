"""Connecteur Audio — enregistrements sonores (métadonnées en V1)."""

from __future__ import annotations

from scc_ingestion.connectors.base import FileSystemConnector
from scc_ingestion.core.models import MediaType


class AudioConnector(FileSystemConnector):
    name = "audio"
    category = "media"
    media_types = (MediaType.AUDIO,)
    extensions = (".mp3", ".wav", ".flac", ".m4a", ".ogg")


__all__ = ["AudioConnector"]
