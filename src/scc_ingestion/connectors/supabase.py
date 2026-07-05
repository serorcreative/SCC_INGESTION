"""Connecteur Supabase — dumps et exports de base (générique).

Découvre des exports SQL/CSV/JSON. La connexion directe (API/Postgres) sera
ajoutée via ``options`` sans modifier l'interface.
"""

from __future__ import annotations

from scc_ingestion.connectors.base import FileSystemConnector
from scc_ingestion.core.models import MediaType


class SupabaseConnector(FileSystemConnector):
    name = "supabase"
    category = "database"
    media_types = (MediaType.JSON, MediaType.CODE, MediaType.TEXT)
    extensions = (".sql", ".json", ".jsonl", ".csv", ".ndjson")
    remote = True
    auto_detect = False  # export base : sélection explicite requise


__all__ = ["SupabaseConnector"]
