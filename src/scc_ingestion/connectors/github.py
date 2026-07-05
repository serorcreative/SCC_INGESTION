"""Connecteur GitHub — dépôts clonés ou exportés (générique).

Traite un dépôt comme une arborescence de fichiers : accepte toutes les
extensions afin de couvrir code, documentation et configuration. La récupération
distante (API) sera branchée ultérieurement via ``options``.
"""

from __future__ import annotations

from scc_ingestion.connectors.base import FileSystemConnector
from scc_ingestion.core.models import MediaType


class GitHubConnector(FileSystemConnector):
    name = "github"
    category = "code"
    media_types = (MediaType.CODE, MediaType.MARKDOWN, MediaType.TEXT)
    extensions = ()  # un dépôt contient des fichiers de toute nature
    remote = True
    auto_detect = False  # dépôt : sélection explicite requise


__all__ = ["GitHubConnector"]
