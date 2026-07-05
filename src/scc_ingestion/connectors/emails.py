"""Connecteur E-mails — messages et archives de courrier."""

from __future__ import annotations

from scc_ingestion.connectors.base import FileSystemConnector
from scc_ingestion.core.models import MediaType


class EmailsConnector(FileSystemConnector):
    name = "emails"
    category = "communication"
    media_types = (MediaType.EMAIL,)
    extensions = (".eml", ".msg", ".olm", ".mbox")


__all__ = ["EmailsConnector"]
