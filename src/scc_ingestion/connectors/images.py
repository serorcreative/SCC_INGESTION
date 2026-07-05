"""Connecteur Images — fichiers graphiques (métadonnées en V1)."""

from __future__ import annotations

from scc_ingestion.connectors.base import FileSystemConnector
from scc_ingestion.core.models import MediaType


class ImagesConnector(FileSystemConnector):
    name = "images"
    category = "media"
    media_types = (MediaType.IMAGE,)
    extensions = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".tif", ".tiff", ".bmp", ".svg")


__all__ = ["ImagesConnector"]
