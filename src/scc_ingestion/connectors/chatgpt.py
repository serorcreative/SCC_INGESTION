"""Connecteur ChatGPT — exports de conversations OpenAI (générique).

Aucune connaissance du schéma OpenAI ici : le connecteur se contente de
découvrir les fichiers d'un export (JSON, Markdown, texte, HTML, archive). Leur
interprétation est faite par les extracteurs génériques du pipeline.
"""

from __future__ import annotations

from scc_ingestion.connectors.base import FileSystemConnector
from scc_ingestion.core.models import MediaType


class ChatGPTConnector(FileSystemConnector):
    name = "chatgpt"
    category = "ia"
    media_types = (MediaType.JSON, MediaType.MARKDOWN, MediaType.TEXT)
    extensions = (".json", ".jsonl", ".md", ".txt", ".html", ".zip")
    remote = True
    auto_detect = False  # export multi-format : sélection explicite requise


__all__ = ["ChatGPTConnector"]
