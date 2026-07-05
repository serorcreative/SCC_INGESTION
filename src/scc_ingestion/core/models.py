"""Modèles de données transitant dans le pipeline.

Ces structures forment le *langage commun* entre connecteurs, étages et
services. Elles sont volontairement neutres : aucune ne connaît une source
particulière. La spécialisation se fait par les champs ``source`` /
``media_type`` / ``metadata``.

Flux type ::

    SourceItem  --(raw copy)-->  RawArtifact
                --(extraction)-> Document
                --(chunking)-->  [Chunk, ...]
                --(cognitive)--> [CognitiveObject, ...]
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class MediaType(str, Enum):
    """Grandes familles de médias, indépendantes du format exact."""

    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"
    DOCUMENT = "document"
    PDF = "pdf"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    EMAIL = "email"
    ARCHIVE = "archive"
    CODE = "code"
    UNKNOWN = "unknown"


def new_id(prefix: str = "obj") -> str:
    """Identifiant court, stable et lisible pour un objet du pipeline."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


@dataclass
class SourceItem:
    """Unité atomique découverte par un connecteur, avant tout traitement.

    ``uri`` désigne l'emplacement d'origine (chemin local, URL, clé d'API…).
    ``source`` est le nom du connecteur émetteur.
    """

    uri: str
    source: str
    media_type: MediaType = MediaType.UNKNOWN
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: new_id("src"))

    @property
    def path(self) -> Optional[Path]:
        """Chemin local si l'``uri`` en est un, sinon ``None``."""
        p = Path(self.uri)
        return p if p.exists() else None


@dataclass
class RawArtifact:
    """Copie brute immuable d'une source, avec son empreinte d'intégrité."""

    raw_path: Path
    sha256: str
    size: int
    origin_uri: str
    media_type: MediaType = MediaType.UNKNOWN
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    """Contenu exploitable extrait d'un artefact brut."""

    text: str
    media_type: MediaType = MediaType.UNKNOWN
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: new_id("doc"))

    @property
    def length(self) -> int:
        return len(self.text)


@dataclass
class Chunk:
    """Fragment de document adapté à l'indexation / au raisonnement."""

    text: str
    index: int
    document_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: new_id("chk"))


@dataclass
class Classification:
    """Étiquetage générique produit par l'étage de classification."""

    category: str = "uncategorized"
    tags: List[str] = field(default_factory=list)
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CognitiveObject:
    """Objet cognitif : unité de connaissance normalisée et indexable.

    C'est la sortie de valeur du moteur ; les couches supérieures de SCC
    (mémoire, raisonnement, API) consomment exclusivement ces objets.
    """

    title: str
    content: str
    category: str = "uncategorized"
    tags: List[str] = field(default_factory=list)
    source: str = "unknown"
    origin_uri: str = ""
    checksum: str = ""
    chunk_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: new_id("cog"))

    def to_dict(self) -> Dict[str, Any]:
        """Sérialisation JSON-compatible (utilisée pour l'indexation)."""
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "tags": list(self.tags),
            "source": self.source,
            "origin_uri": self.origin_uri,
            "checksum": self.checksum,
            "chunk_ids": list(self.chunk_ids),
            "metadata": dict(self.metadata),
            "content": self.content,
        }


__all__ = [
    "MediaType",
    "new_id",
    "SourceItem",
    "RawArtifact",
    "Document",
    "Chunk",
    "Classification",
    "CognitiveObject",
]
