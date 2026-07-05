"""Contrat des watchers de source.

En V1, seule l'**infrastructure** de détection est fournie : un watcher sait
comparer l'état courant d'une arborescence à un instantané précédent et lister
les nouveautés (:meth:`scan`). L'automatisation (boucle, threads, planification)
est délibérément *hors périmètre* et branchera :meth:`scan` plus tard.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class WatchEvent:
    """Événement de détection : un fichier apparu ou modifié."""

    path: Path
    kind: str  # "created" | "modified"
    size: int
    modified: float


class Watcher(ABC):
    """Détecteur de nouveautés sur une source, sans boucle d'automatisation."""

    @abstractmethod
    def scan(self) -> List[WatchEvent]:
        """Retourne les événements depuis le dernier :meth:`scan` (et met à jour l'état)."""
        raise NotImplementedError

    def start(self) -> None:
        """Réservé à la V2 (surveillance continue)."""
        raise NotImplementedError(
            "L'automatisation des watchers est prévue en V2. Utilisez scan() pour "
            "une détection ponctuelle."
        )

    def stop(self) -> None:
        """Réservé à la V2 (surveillance continue)."""
        raise NotImplementedError(
            "L'automatisation des watchers est prévue en V2."
        )


__all__ = ["Watcher", "WatchEvent"]
