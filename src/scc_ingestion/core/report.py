"""Rapport générique du moteur d'ingestion.

Reprend et étend le contrat ``Report`` / ``Check`` déjà utilisé par SC CLI afin
que l'ensemble de l'écosystème Seror Créative partage la même sémantique de
compte rendu.
"""

from __future__ import annotations

from collections import namedtuple
from typing import Any, Dict, Iterable, List, Optional

# Résultat unitaire d'une vérification ou d'un étage.
Check = namedtuple("Check", ["label", "passed", "detail"])


class Report:
    """Agrège une série de :class:`Check` et expose un statut global ``ok``."""

    def __init__(self, title: str, checks: Optional[Iterable[Check]] = None):
        self.title = title
        self.checks: List[Check] = list(checks) if checks else []

    @property
    def ok(self) -> bool:
        """Vrai si aucune vérification n'a échoué (rapport vide = ``True``)."""
        return all(check.passed for check in self.checks)

    def add(self, label: str, passed: bool, detail: str = "") -> Check:
        """Ajoute une vérification et la retourne."""
        check = Check(label, passed, detail)
        self.checks.append(check)
        return check

    def merge(self, other: "Report") -> "Report":
        """Fusionne les vérifications d'un autre rapport dans celui-ci."""
        self.checks.extend(other.checks)
        return self

    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for c in self.checks if not c.passed)

    def to_dict(self) -> Dict[str, Any]:
        """Sérialisation JSON-compatible du rapport."""
        return {
            "title": self.title,
            "ok": self.ok,
            "passed": self.passed_count,
            "failed": self.failed_count,
            "checks": [
                {"label": c.label, "passed": c.passed, "detail": c.detail}
                for c in self.checks
            ],
        }

    def __repr__(self) -> str:  # pragma: no cover - confort de débogage
        return f"<Report {self.title!r} ok={self.ok} checks={len(self.checks)}>"


__all__ = ["Check", "Report"]
