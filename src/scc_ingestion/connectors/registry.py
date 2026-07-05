"""Registre des connecteurs disponibles.

Point d'entrée unique pour découvrir, instancier et étendre l'ensemble des
connecteurs. Les nouveaux connecteurs s'ajoutent via :meth:`ConnectorRegistry.register`
sans toucher au reste du moteur.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Type

from scc_ingestion.connectors.audio import AudioConnector
from scc_ingestion.connectors.base import Connector
from scc_ingestion.connectors.base44 import Base44Connector
from scc_ingestion.connectors.chatgpt import ChatGPTConnector
from scc_ingestion.connectors.claude import ClaudeConnector
from scc_ingestion.connectors.documents import DocumentsConnector
from scc_ingestion.connectors.emails import EmailsConnector
from scc_ingestion.connectors.github import GitHubConnector
from scc_ingestion.connectors.images import ImagesConnector
from scc_ingestion.connectors.markdown import MarkdownConnector
from scc_ingestion.connectors.pdf import PdfConnector
from scc_ingestion.connectors.supabase import SupabaseConnector
from scc_ingestion.connectors.video import VideoConnector
from scc_ingestion.core.errors import ConnectorError

# Connecteurs livrés en V1, dans l'ordre d'affichage.
BUILTIN_CONNECTORS: List[Type[Connector]] = [
    ChatGPTConnector,
    ClaudeConnector,
    GitHubConnector,
    SupabaseConnector,
    Base44Connector,
    DocumentsConnector,
    PdfConnector,
    MarkdownConnector,
    ImagesConnector,
    AudioConnector,
    VideoConnector,
    EmailsConnector,
]


class ConnectorRegistry:
    """Table de correspondance ``name -> classe de connecteur``."""

    def __init__(self, connectors: Optional[Iterable[Type[Connector]]] = None):
        self._classes: Dict[str, Type[Connector]] = {}
        for cls in connectors if connectors is not None else BUILTIN_CONNECTORS:
            self.register(cls)

    def register(self, connector_cls: Type[Connector]) -> None:
        """Enregistre (ou remplace) un connecteur par son ``name``."""
        name = connector_cls.name
        if not name or name == "abstract":
            raise ConnectorError(f"Connecteur sans nom valide : {connector_cls!r}")
        self._classes[name] = connector_cls

    def available(self) -> List[str]:
        """Noms des connecteurs enregistrés."""
        return list(self._classes.keys())

    def has(self, name: str) -> bool:
        return name in self._classes

    def get(self, name: str, options: Optional[Dict[str, Any]] = None) -> Connector:
        """Instancie un connecteur par son nom."""
        if name not in self._classes:
            raise ConnectorError(
                f"Connecteur inconnu : {name!r} (disponibles : {', '.join(self.available())})"
            )
        return self._classes[name](options)

    def for_path(self, path, options: Optional[Dict[str, Any]] = None) -> Optional[Connector]:
        """Retourne le connecteur auto-détectable le plus *spécifique* pour ``path``.

        Sont éligibles les connecteurs à extensions déclarées et marqués
        ``auto_detect`` (les agrégateurs multi-formats en sont exclus : ils
        exigent une sélection explicite). En cas de multiples candidats, le plus
        spécialisé gagne (plus petit jeu d'extensions).
        """
        candidates = [
            c for c in self._classes.values() if c.extensions and c.auto_detect
        ]
        candidates.sort(key=lambda c: len(c.extensions))
        for cls in candidates:
            probe = cls(options)
            if probe.supports(path):
                return probe
        return None

    def describe_all(self) -> List[Dict[str, Any]]:
        return [cls(None).describe() for cls in self._classes.values()]


# Registre par défaut, prêt à l'emploi.
default_registry = ConnectorRegistry()


__all__ = ["ConnectorRegistry", "BUILTIN_CONNECTORS", "default_registry"]
