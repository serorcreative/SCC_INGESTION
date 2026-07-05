"""Watcher de système de fichiers pour ``02_RAW_SOURCES`` (détection ponctuelle).

Maintient un instantané JSON (chemin → taille + date de modification) et, à
chaque :meth:`scan`, retourne les fichiers *apparus* ou *modifiés* depuis le
dernier appel, puis met à jour l'instantané. Aucune boucle, aucun thread : c'est
l'infrastructure sur laquelle l'automatisation V2 se branchera.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Union

from scc_ingestion.watchers.base import WatchEvent, Watcher


class FileSystemWatcher(Watcher):
    """Détecte les nouveaux fichiers d'une arborescence par comparaison d'état."""

    def __init__(
        self,
        root: Union[str, Path],
        state_path: Optional[Union[str, Path]] = None,
    ):
        self.root = Path(root)
        # État persistant par défaut à côté de la racine surveillée.
        self.state_path = (
            Path(state_path)
            if state_path
            else self.root.parent / f".watch_{self.root.name}.json"
        )

    def _load_state(self) -> Dict[str, list]:
        if not self.state_path.exists():
            return {}
        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def _save_state(self, state: Dict[str, list]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _current(self) -> Dict[str, list]:
        state: Dict[str, list] = {}
        if not self.root.exists():
            return state
        for path in sorted(p for p in self.root.rglob("*") if p.is_file()):
            if path.name.startswith("."):
                continue
            stat = path.stat()
            state[str(path)] = [stat.st_size, stat.st_mtime]
        return state

    def scan(self, persist: bool = True) -> List[WatchEvent]:
        """Compare l'état courant à l'instantané et retourne les nouveautés."""
        previous = self._load_state()
        current = self._current()

        events: List[WatchEvent] = []
        for key, (size, mtime) in current.items():
            if key not in previous:
                events.append(WatchEvent(Path(key), "created", size, mtime))
            elif previous[key] != [size, mtime]:
                events.append(WatchEvent(Path(key), "modified", size, mtime))

        if persist:
            self._save_state(current)
        return events


__all__ = ["FileSystemWatcher"]
