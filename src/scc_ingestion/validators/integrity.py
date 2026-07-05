"""Contrôle d'intégrité d'une source locale.

Vérifie qu'un chemin existe, est un fichier lisible et non vide, puis calcule
son empreinte. Le résultat est un :class:`Report` réutilisable partout.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple, Union

from scc_ingestion.core.report import Report
from scc_ingestion.validators.hashing import sha256_file


def check_integrity(path: Union[str, Path]) -> Tuple[Report, Optional[str]]:
    """Contrôle l'intégrité d'un fichier.

    Retourne ``(report, sha256)``. ``sha256`` vaut ``None`` si l'empreinte n'a
    pas pu être calculée (le rapport porte alors le détail de l'échec).
    """
    target = Path(path)
    report = Report(f"Intégrité — {target.name}")

    exists = target.exists()
    report.add("existence", exists, str(target))
    if not exists:
        return report, None

    is_file = target.is_file()
    report.add("est un fichier", is_file, "" if is_file else "chemin non-fichier")
    if not is_file:
        return report, None

    try:
        size = target.stat().st_size
    except OSError as exc:
        report.add("lisible", False, str(exc))
        return report, None

    report.add("non vide", size > 0, f"{size} octets")

    try:
        digest = sha256_file(target)
        report.add("empreinte sha256", True, digest)
        return report, digest
    except OSError as exc:
        report.add("empreinte sha256", False, str(exc))
        return report, None


__all__ = ["check_integrity"]
