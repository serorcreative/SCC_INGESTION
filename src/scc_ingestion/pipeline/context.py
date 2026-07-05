"""Contexte d'ingestion : l'« enveloppe » qui traverse tout le pipeline.

Chaque étage lit et enrichit ce contexte. Il concentre l'état d'une exécution
(un ``SourceItem`` du début à la fin) et son rapport cumulé, ce qui rend les
étages indépendants et testables isolément.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from scc_ingestion.core.config import IngestionConfig
from scc_ingestion.core.models import (
    Chunk,
    Classification,
    CognitiveObject,
    Document,
    RawArtifact,
    SourceItem,
    new_id,
)
from scc_ingestion.core.report import Report


@dataclass
class IngestionContext:
    """État mutable d'une exécution du pipeline pour un ``SourceItem``."""

    source_item: SourceItem
    config: IngestionConfig
    run_id: str = field(default_factory=lambda: new_id("run"))

    # Remplis progressivement par les étages.
    raw_artifact: Optional[RawArtifact] = None
    extracted_files: List[Path] = field(default_factory=list)
    document: Optional[Document] = None
    normalized_text: Optional[str] = None
    chunks: List[Chunk] = field(default_factory=list)
    classification: Optional[Classification] = None
    cognitive_objects: List[CognitiveObject] = field(default_factory=list)

    report: Report = field(default_factory=lambda: Report("Ingestion"))
    metadata: Dict[str, Any] = field(default_factory=dict)
    aborted: bool = False

    @property
    def workdir(self) -> Path:
        """Répertoire de travail isolé de cette exécution (créé à la demande)."""
        path = self.config.work_root / "runs" / self.run_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def abort(self, reason: str) -> None:
        """Marque le contexte comme interrompu (le pipeline s'arrêtera)."""
        self.aborted = True
        self.metadata["abort_reason"] = reason


__all__ = ["IngestionContext"]
