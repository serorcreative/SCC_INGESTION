"""Décompression générique d'archives (zip, tar, tar.gz/bz2, gzip).

Repose exclusivement sur la bibliothèque standard. La fonction :func:`decompress`
protège contre la traversée de chemins (« zip slip ») en refusant toute entrée
qui sortirait du répertoire de destination.
"""

from __future__ import annotations

import gzip
import shutil
import tarfile
import zipfile
from pathlib import Path
from typing import List, Union

from scc_ingestion.core.errors import DecompressionError

_ARCHIVE_SUFFIXES = {".zip", ".tar", ".gz", ".tgz", ".bz2", ".tbz2"}


def is_archive(path: Union[str, Path]) -> bool:
    """Vrai si le fichier a une extension d'archive reconnue."""
    p = Path(path)
    if p.suffix.lower() in _ARCHIVE_SUFFIXES:
        return True
    # Cas .tar.gz / .tar.bz2
    return "".join(p.suffixes[-2:]).lower() in {".tar.gz", ".tar.bz2"}


def _is_within(base: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def decompress(path: Union[str, Path], dest: Union[str, Path]) -> List[Path]:
    """Décompresse ``path`` dans ``dest`` et retourne la liste des fichiers extraits.

    Lève :class:`DecompressionError` si le format est inconnu ou si une entrée
    tente de sortir de ``dest``.
    """
    src = Path(path)
    out = Path(dest)
    out.mkdir(parents=True, exist_ok=True)
    suffixes = "".join(src.suffixes[-2:]).lower()

    try:
        if zipfile.is_zipfile(src):
            with zipfile.ZipFile(src) as zf:
                for name in zf.namelist():
                    if not _is_within(out, out / name):
                        raise DecompressionError(f"Entrée d'archive non sûre : {name}")
                zf.extractall(out)
        elif tarfile.is_tarfile(src):
            with tarfile.open(src) as tf:
                for member in tf.getmembers():
                    if not _is_within(out, out / member.name):
                        raise DecompressionError(f"Entrée d'archive non sûre : {member.name}")
                tf.extractall(out)
        elif suffixes.endswith(".gz") or src.suffix.lower() == ".gz":
            target = out / src.with_suffix("").name
            with gzip.open(src, "rb") as gz, open(target, "wb") as handle:
                shutil.copyfileobj(gz, handle)
        else:
            raise DecompressionError(f"Format d'archive non pris en charge : {src.name}")
    except (OSError, tarfile.TarError, zipfile.BadZipFile) as exc:
        raise DecompressionError(f"Échec de décompression ({src.name}) : {exc}") from exc

    return [p for p in out.rglob("*") if p.is_file()]


__all__ = ["is_archive", "decompress"]
