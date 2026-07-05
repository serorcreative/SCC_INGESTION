"""Contrat d'un étage de pipeline.

Un étage lit/enrichit le :class:`IngestionContext` et signale son résultat en
ajoutant **exactement une** vérification à ``ctx.report`` lorsqu'il réussit. En
cas d'échec fatal, il lève une :class:`IngestionError` : l'orchestrateur la
capture et enregistre l'échec (voir :mod:`scc_ingestion.pipeline.pipeline`).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from scc_ingestion.pipeline.context import IngestionContext


class Stage(ABC):
    """Étage atomique et indépendant du pipeline."""

    #: Libellé de l'étage, utilisé dans le rapport et les journaux.
    name: str = "stage"

    @abstractmethod
    def run(self, ctx: IngestionContext) -> None:
        """Exécute l'étage en mutant ``ctx``."""
        raise NotImplementedError

    def _ok(self, ctx: IngestionContext, detail: str = "") -> None:
        """Raccourci : enregistre le succès de l'étage."""
        ctx.report.add(self.name, True, detail)

    def __repr__(self) -> str:  # pragma: no cover - confort de débogage
        return f"<Stage {self.name}>"


__all__ = ["Stage"]
