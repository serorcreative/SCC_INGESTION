"""Connecteurs de source — tous conformes à l'interface :class:`Connector`."""

from __future__ import annotations

from scc_ingestion.connectors.base import Connector, FileSystemConnector
from scc_ingestion.connectors.registry import (
    BUILTIN_CONNECTORS,
    ConnectorRegistry,
    default_registry,
)

__all__ = [
    "Connector",
    "FileSystemConnector",
    "ConnectorRegistry",
    "BUILTIN_CONNECTORS",
    "default_registry",
]
