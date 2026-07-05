"""Watchers — infrastructure de détection des nouvelles sources (V1 : ponctuelle)."""

from __future__ import annotations

from scc_ingestion.watchers.base import WatchEvent, Watcher
from scc_ingestion.watchers.filesystem import FileSystemWatcher

__all__ = ["Watcher", "WatchEvent", "FileSystemWatcher"]
