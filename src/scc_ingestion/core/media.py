"""Détection générique du type de média à partir de l'extension de fichier.

Volontairement basée sur l'extension (rapide, sans dépendance) et centralisée
ici pour que connecteurs et étages partagent la même table de correspondance.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from scc_ingestion.core.models import MediaType

# Correspondance extension (minuscule, avec le point) -> MediaType.
_EXTENSION_MAP: Dict[str, MediaType] = {
    ".txt": MediaType.TEXT,
    ".log": MediaType.TEXT,
    ".md": MediaType.MARKDOWN,
    ".markdown": MediaType.MARKDOWN,
    ".json": MediaType.JSON,
    ".jsonl": MediaType.JSON,
    ".ndjson": MediaType.JSON,
    ".pdf": MediaType.PDF,
    ".doc": MediaType.DOCUMENT,
    ".docx": MediaType.DOCUMENT,
    ".odt": MediaType.DOCUMENT,
    ".rtf": MediaType.DOCUMENT,
    ".xls": MediaType.DOCUMENT,
    ".xlsx": MediaType.DOCUMENT,
    ".ppt": MediaType.DOCUMENT,
    ".pptx": MediaType.DOCUMENT,
    ".png": MediaType.IMAGE,
    ".jpg": MediaType.IMAGE,
    ".jpeg": MediaType.IMAGE,
    ".gif": MediaType.IMAGE,
    ".webp": MediaType.IMAGE,
    ".tif": MediaType.IMAGE,
    ".tiff": MediaType.IMAGE,
    ".bmp": MediaType.IMAGE,
    ".svg": MediaType.IMAGE,
    ".mp3": MediaType.AUDIO,
    ".wav": MediaType.AUDIO,
    ".flac": MediaType.AUDIO,
    ".m4a": MediaType.AUDIO,
    ".ogg": MediaType.AUDIO,
    ".mp4": MediaType.VIDEO,
    ".mov": MediaType.VIDEO,
    ".mkv": MediaType.VIDEO,
    ".avi": MediaType.VIDEO,
    ".webm": MediaType.VIDEO,
    ".eml": MediaType.EMAIL,
    ".msg": MediaType.EMAIL,
    ".olm": MediaType.EMAIL,
    ".mbox": MediaType.EMAIL,
    ".zip": MediaType.ARCHIVE,
    ".tar": MediaType.ARCHIVE,
    ".gz": MediaType.ARCHIVE,
    ".tgz": MediaType.ARCHIVE,
    ".bz2": MediaType.ARCHIVE,
    ".py": MediaType.CODE,
    ".js": MediaType.CODE,
    ".ts": MediaType.CODE,
    ".sql": MediaType.CODE,
    ".sh": MediaType.CODE,
    ".html": MediaType.CODE,
    ".css": MediaType.CODE,
    ".yaml": MediaType.CODE,
    ".yml": MediaType.CODE,
    ".toml": MediaType.CODE,
}


def detect_media_type(path) -> MediaType:
    """Déduit le :class:`MediaType` d'un chemin à partir de son extension."""
    suffix = Path(path).suffix.lower()
    return _EXTENSION_MAP.get(suffix, MediaType.UNKNOWN)


def extensions_for(media_type: MediaType) -> tuple:
    """Retourne le tuple des extensions connues pour un ``media_type``."""
    return tuple(ext for ext, mt in _EXTENSION_MAP.items() if mt == media_type)


__all__ = ["detect_media_type", "extensions_for"]
