"""Tests du watcher de système de fichiers (détection ponctuelle)."""

from __future__ import annotations

import time
from pathlib import Path

from scc_ingestion.watchers.base import Watcher
from scc_ingestion.watchers.filesystem import FileSystemWatcher


def test_scan_detects_new_files(tmp_path: Path):
    root = tmp_path / "raw"
    root.mkdir()
    state = tmp_path / "state.json"
    watcher = FileSystemWatcher(root, state_path=state)

    # Premier scan : tout est nouveau.
    (root / "a.txt").write_text("a", encoding="utf-8")
    events = watcher.scan()
    assert len(events) == 1
    assert events[0].kind == "created"

    # Deuxième scan sans changement : rien.
    assert watcher.scan() == []

    # Ajout d'un fichier : détecté.
    (root / "b.txt").write_text("b", encoding="utf-8")
    events = watcher.scan()
    assert len(events) == 1
    assert events[0].path.name == "b.txt"


def test_scan_detects_modification(tmp_path: Path):
    root = tmp_path / "raw"
    root.mkdir()
    watcher = FileSystemWatcher(root, state_path=tmp_path / "s.json")
    f = root / "a.txt"
    f.write_text("a", encoding="utf-8")
    watcher.scan()

    time.sleep(0.01)
    f.write_text("a much longer content", encoding="utf-8")
    events = watcher.scan()
    assert len(events) == 1
    assert events[0].kind == "modified"


def test_dry_run_does_not_persist(tmp_path: Path):
    root = tmp_path / "raw"
    root.mkdir()
    (root / "a.txt").write_text("a", encoding="utf-8")
    watcher = FileSystemWatcher(root, state_path=tmp_path / "s.json")
    assert len(watcher.scan(persist=False)) == 1
    # État non mémorisé -> toujours vu comme nouveau.
    assert len(watcher.scan(persist=False)) == 1


def test_scan_missing_root_is_empty(tmp_path: Path):
    watcher = FileSystemWatcher(tmp_path / "absent", state_path=tmp_path / "s.json")
    assert watcher.scan() == []


def test_start_not_implemented_in_v1(tmp_path: Path):
    watcher = FileSystemWatcher(tmp_path, state_path=tmp_path / "s.json")
    assert isinstance(watcher, Watcher)
    try:
        watcher.start()
        raised = False
    except NotImplementedError:
        raised = True
    assert raised
