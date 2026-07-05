"""Connecteur PDF — documents portables."""

from __future__ import annotations

from scc_ingestion.connectors.base import FileSystemConnector
from scc_ingestion.core.models import MediaType


class PdfConnector(FileSystemConnector):
    name = "pdf"
    category = "document"
    media_types = (MediaType.PDF,)
    extensions = (".pdf",)


__all__ = ["PdfConnector"]
