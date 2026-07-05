"""Interface commune à tous les connecteurs de source.

Un connecteur est un *adaptateur* : il sait **découvrir** des unités
(:class:`SourceItem`) depuis une source, et **récupérer** leur charge utile
brute (octets). Il ne fait rien d'autre — extraction, normalisation et
classification sont la responsabilité du pipeline, garantissant qu'aucune
logique spécifique à un fournisseur ne fuite hors du connecteur.

Deux niveaux :

* :class:`Connector` — contrat abstrait (``discover`` + ``fetch``).
* :class:`FileSystemConnector` — implémentation générique sur le système de
  fichiers, dont héritent tous les connecteurs livrés en V1. Chaque connecteur
  concret se contente de déclarer son ``name``, sa ``category``, ses
  ``media_types`` et ses ``extensions``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, Optional, Tuple, Union

from scc_ingestion.core.errors import ConnectorError
from scc_ingestion.core.media import detect_media_type
from scc_ingestion.core.models import MediaType, SourceItem

# Une « source » est, en V1, un chemin local (fichier ou répertoire).
SourceSpec = Union[str, Path]


class Connector(ABC):
    """Contrat abstrait que tout connecteur doit respecter."""

    #: Identifiant unique et stable du connecteur (clé de registre).
    name: str = "abstract"
    #: Catégorie fonctionnelle (ex. « ia », « code », « media », « document »).
    category: str = "generic"
    #: Types de médias que le connecteur revendique.
    media_types: Tuple[MediaType, ...] = ()
    #: Extensions gérées (vide = toutes).
    extensions: Tuple[str, ...] = ()
    #: Vrai si la source est distante (API) — informatif pour la V1 locale.
    remote: bool = False
    #: Vrai si le connecteur peut être choisi par auto-détection d'extension.
    #: Les agrégateurs multi-formats (IA, dépôts, apps) le passent à ``False``
    #: car ils requièrent une sélection explicite (``--source``).
    auto_detect: bool = True

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        self.options: Dict[str, Any] = dict(options or {})

    @abstractmethod
    def discover(self, source: SourceSpec) -> Iterable[SourceItem]:
        """Énumère les :class:`SourceItem` disponibles dans ``source``."""
        raise NotImplementedError

    @abstractmethod
    def fetch(self, item: SourceItem) -> bytes:
        """Retourne la charge utile brute (octets) d'un ``item``."""
        raise NotImplementedError

    def supports(self, path: SourceSpec) -> bool:
        """Indique si le connecteur peut traiter ``path`` (filtrage par extension)."""
        if not self.extensions:
            return True
        return Path(path).suffix.lower() in self.extensions

    def describe(self) -> Dict[str, Any]:
        """Métadonnées descriptives du connecteur (pour la CLI / les rapports)."""
        return {
            "name": self.name,
            "category": self.category,
            "media_types": [mt.value for mt in self.media_types],
            "extensions": list(self.extensions),
            "remote": self.remote,
            "auto_detect": self.auto_detect,
        }

    def __repr__(self) -> str:  # pragma: no cover - confort de débogage
        return f"<Connector {self.name} category={self.category}>"


class FileSystemConnector(Connector):
    """Connecteur générique lisant des fichiers depuis le système de fichiers.

    ``discover`` parcourt un répertoire (ou accepte un fichier isolé) en
    filtrant par extensions déclarées ; ``fetch`` lit les octets du fichier.
    """

    def discover(self, source: SourceSpec) -> Iterator[SourceItem]:
        root = Path(source).expanduser()
        if not root.exists():
            raise ConnectorError(f"Source introuvable : {root}")

        candidates: Iterable[Path]
        if root.is_file():
            candidates = [root]
        else:
            candidates = sorted(p for p in root.rglob("*") if p.is_file())

        for path in candidates:
            if path.name.startswith(".") or path.name == "Icon\r":
                continue  # ignore fichiers cachés et artefacts macOS
            if not self.supports(path):
                continue
            media_type = detect_media_type(path)
            yield SourceItem(
                uri=str(path),
                source=self.name,
                media_type=media_type,
                metadata={
                    "filename": path.name,
                    "connector": self.name,
                    "category": self.category,
                },
            )

    def fetch(self, item: SourceItem) -> bytes:
        path = Path(item.uri)
        if not path.is_file():
            raise ConnectorError(f"Charge utile introuvable : {path}")
        try:
            return path.read_bytes()
        except OSError as exc:
            raise ConnectorError(f"Lecture impossible ({path}) : {exc}") from exc


__all__ = ["Connector", "FileSystemConnector", "SourceSpec"]
