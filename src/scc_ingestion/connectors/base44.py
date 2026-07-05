"""Connecteur Base44 — exports d'applications (générique).

Découvre les artefacts d'un export Base44 (archives, JSON de configuration,
code, documentation). Aucune hypothèse sur le format interne.
"""

from __future__ import annotations

from scc_ingestion.connectors.base import FileSystemConnector
from scc_ingestion.core.models import MediaType


class Base44Connector(FileSystemConnector):
    name = "base44"
    category = "app"
    media_types = (MediaType.JSON, MediaType.CODE, MediaType.ARCHIVE)
    extensions = (".json", ".zip", ".js", ".ts", ".html", ".css", ".md")
    remote = True
    auto_detect = False  # export applicatif : sélection explicite requise


__all__ = ["Base44Connector"]
