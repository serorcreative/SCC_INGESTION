"""Chargement et valeurs par défaut de la configuration du moteur.

Le format retenu est le JSON (stdlib, sans dépendance). La configuration décrit
uniquement des *chemins* et des *paramètres génériques* — jamais de logique
propre à une source.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from scc_ingestion.core.errors import ConfigError

# Racine du moteur : .../01_INGESTION (deux niveaux au-dessus de ce fichier =
# src/scc_ingestion/core/config.py -> core -> scc_ingestion -> src -> 01_INGESTION)
ENGINE_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_CONFIG_PATH = ENGINE_ROOT / "config" / "ingestion.json"


@dataclass
class ChunkingConfig:
    """Paramètres de découpage du texte normalisé."""

    max_chars: int = 2000
    overlap: int = 200
    min_chars: int = 1


@dataclass
class IngestionConfig:
    """Configuration complète du moteur.

    Tous les chemins sont résolus en absolu et relatifs à ``engine_root`` quand
    ils sont fournis en relatif.
    """

    engine_root: Path = ENGINE_ROOT
    raw_sources_root: Path = ENGINE_ROOT.parent / "02_RAW_SOURCES"
    work_root: Path = ENGINE_ROOT / "queue"
    reports_dir: Path = ENGINE_ROOT / "reports"
    logs_dir: Path = ENGINE_ROOT / "logs"
    archive_dir: Path = ENGINE_ROOT / "queue" / "_archive"
    index_path: Path = ENGINE_ROOT / "queue" / "index.jsonl"
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    enabled_sources: List[str] = field(default_factory=list)
    classification_rules: Dict[str, List[str]] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)

    def ensure_directories(self) -> None:
        """Crée les répertoires runtime nécessaires (idempotent)."""
        for directory in (
            self.work_root,
            self.reports_dir,
            self.logs_dir,
            self.archive_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        for key, value in data.items():
            if isinstance(value, Path):
                data[key] = str(value)
        return data


def _resolve(base: Path, value: str) -> Path:
    p = Path(value).expanduser()
    return p if p.is_absolute() else (base / p).resolve()


def load_config(path: Optional[Path] = None) -> IngestionConfig:
    """Charge la configuration depuis un fichier JSON, avec repli sur les défauts.

    Si ``path`` est ``None`` et que le fichier par défaut n'existe pas, une
    configuration entièrement par défaut est retournée (le moteur reste
    utilisable sans fichier de config).
    """
    config = IngestionConfig()

    target = Path(path) if path else DEFAULT_CONFIG_PATH
    if not target.exists():
        if path is not None:
            raise ConfigError(f"Configuration introuvable : {target}")
        return config

    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"Configuration illisible ({target}) : {exc}") from exc

    base = config.engine_root
    paths = raw.get("paths", {})
    if "raw_sources_root" in paths:
        config.raw_sources_root = _resolve(base, paths["raw_sources_root"])
    if "work_root" in paths:
        config.work_root = _resolve(base, paths["work_root"])
    if "reports_dir" in paths:
        config.reports_dir = _resolve(base, paths["reports_dir"])
    if "logs_dir" in paths:
        config.logs_dir = _resolve(base, paths["logs_dir"])
    if "archive_dir" in paths:
        config.archive_dir = _resolve(base, paths["archive_dir"])
    if "index_path" in paths:
        config.index_path = _resolve(base, paths["index_path"])

    chunking = raw.get("chunking", {})
    config.chunking = ChunkingConfig(
        max_chars=int(chunking.get("max_chars", ChunkingConfig.max_chars)),
        overlap=int(chunking.get("overlap", ChunkingConfig.overlap)),
        min_chars=int(chunking.get("min_chars", ChunkingConfig.min_chars)),
    )

    config.enabled_sources = list(raw.get("enabled_sources", []))
    config.classification_rules = dict(raw.get("classification_rules", {}))
    config.extra = dict(raw.get("extra", {}))
    return config


__all__ = ["ENGINE_ROOT", "DEFAULT_CONFIG_PATH", "ChunkingConfig", "IngestionConfig", "load_config"]
