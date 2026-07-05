"""Connecteur Documents — bureautique (Word, Excel, PowerPoint, RTF, ODT…)."""

from __future__ import annotations

from scc_ingestion.connectors.base import FileSystemConnector
from scc_ingestion.core.models import MediaType


class DocumentsConnector(FileSystemConnector):
    name = "documents"
    category = "document"
    media_types = (MediaType.DOCUMENT, MediaType.TEXT)
    extensions = (
        ".doc", ".docx", ".odt", ".rtf",
        ".xls", ".xlsx", ".ppt", ".pptx",
        ".txt",
    )


__all__ = ["DocumentsConnector"]
