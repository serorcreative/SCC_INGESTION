"""Empreintes cryptographiques (SHA-256) pour le contrôle d'intégrité.

Une seule responsabilité : produire et vérifier des empreintes stables, sans
charger l'intégralité d'un fichier en mémoire (lecture par blocs).
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Union

_CHUNK = 1024 * 1024  # 1 Mio


def sha256_bytes(data: bytes) -> str:
    """Empreinte SHA-256 d'un buffer d'octets."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Union[str, Path]) -> str:
    """Empreinte SHA-256 d'un fichier, lu par blocs de 1 Mio."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(_CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_file(path: Union[str, Path], expected: str) -> bool:
    """Vrai si l'empreinte du fichier correspond à ``expected`` (insensible à la casse)."""
    return sha256_file(path).lower() == expected.lower()


__all__ = ["sha256_bytes", "sha256_file", "verify_file"]
