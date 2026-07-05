"""Inventaire d'un répertoire ou d'un ensemble de fichiers.

Produit une liste d'entrées (chemin relatif, taille, empreinte, date de
modification) exploitable pour la traçabilité et la détection de doublons.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Union

from scc_ingestion.validators.hashing import sha256_file


@dataclass
class InventoryEntry:
    """Une ligne d'inventaire pour un fichier."""

    relative_path: str
    size: int
    sha256: str
    modified: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_inventory(root: Union[str, Path], with_hash: bool = True) -> List[InventoryEntry]:
    """Construit l'inventaire récursif de ``root``.

    Si ``root`` est un fichier, l'inventaire ne contient que ce fichier. Les
    empreintes ne sont calculées que si ``with_hash`` est vrai (utile pour de
    gros volumes où l'on ne veut qu'un décompte).
    """
    base = Path(root)
    if base.is_file():
        files = [base]
        anchor = base.parent
    else:
        files = sorted(p for p in base.rglob("*") if p.is_file())
        anchor = base

    entries: List[InventoryEntry] = []
    for f in files:
        stat = f.stat()
        entries.append(
            InventoryEntry(
                relative_path=str(f.relative_to(anchor)),
                size=stat.st_size,
                sha256=sha256_file(f) if with_hash else "",
                modified=stat.st_mtime,
            )
        )
    return entries


__all__ = ["InventoryEntry", "build_inventory"]
