"""Connecteur Markdown — notes et documentation."""

from __future__ import annotations

from scc_ingestion.connectors.base import FileSystemConnector
from scc_ingestion.core.models import MediaType


class MarkdownConnector(FileSystemConnector):
    name = "markdown"
    category = "document"
    media_types = (MediaType.MARKDOWN,)
    extensions = (".md", ".markdown")


__all__ = ["MarkdownConnector"]
