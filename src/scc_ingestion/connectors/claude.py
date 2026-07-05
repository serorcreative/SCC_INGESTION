"""Connecteur Claude — exports de conversations Anthropic (générique).

Comme tous les connecteurs IA, il découvre des fichiers d'export et délègue
toute interprétation au pipeline. Aucune spécificité de fournisseur.
"""

from __future__ import annotations

from scc_ingestion.connectors.base import FileSystemConnector
from scc_ingestion.core.models import MediaType


class ClaudeConnector(FileSystemConnector):
    name = "claude"
    category = "ia"
    media_types = (MediaType.JSON, MediaType.MARKDOWN, MediaType.TEXT)
    extensions = (".json", ".jsonl", ".md", ".txt", ".html", ".zip")
    remote = True
    auto_detect = False  # export multi-format : sélection explicite requise


__all__ = ["ClaudeConnector"]
