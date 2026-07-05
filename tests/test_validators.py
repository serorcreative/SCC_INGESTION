"""Tests des validators : hash, intégrité, décompression, inventaire."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from scc_ingestion.core.errors import DecompressionError
from scc_ingestion.validators.decompression import decompress, is_archive
from scc_ingestion.validators.hashing import sha256_bytes, sha256_file, verify_file
from scc_ingestion.validators.integrity import check_integrity
from scc_ingestion.validators.inventory import build_inventory


def test_hashing_bytes_and_file(tmp_path: Path):
    f = tmp_path / "a.txt"
    f.write_bytes(b"hello")
    assert sha256_file(f) == sha256_bytes(b"hello")
    assert verify_file(f, sha256_bytes(b"hello"))
    assert not verify_file(f, "0" * 64)


def test_integrity_ok(tmp_path: Path):
    f = tmp_path / "a.txt"
    f.write_text("content", encoding="utf-8")
    report, digest = check_integrity(f)
    assert report.ok
    assert digest and len(digest) == 64


def test_integrity_missing(tmp_path: Path):
    report, digest = check_integrity(tmp_path / "none.txt")
    assert not report.ok
    assert digest is None


def test_integrity_empty_file_flagged(tmp_path: Path):
    f = tmp_path / "empty.txt"
    f.write_bytes(b"")
    report, _ = check_integrity(f)
    assert not report.ok  # "non vide" échoue


def test_is_archive():
    assert is_archive("x.zip")
    assert is_archive("x.tar.gz")
    assert not is_archive("x.txt")


def test_decompress_zip(tmp_path: Path):
    archive = tmp_path / "a.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("inner/file.txt", "data")
    out = decompress(archive, tmp_path / "out")
    assert any(p.name == "file.txt" for p in out)


def test_decompress_unknown_format(tmp_path: Path):
    bogus = tmp_path / "a.txt"
    bogus.write_text("not an archive", encoding="utf-8")
    with pytest.raises(DecompressionError):
        decompress(bogus, tmp_path / "out")


def test_inventory(tmp_path: Path):
    (tmp_path / "d").mkdir()
    (tmp_path / "d" / "1.txt").write_text("a", encoding="utf-8")
    (tmp_path / "d" / "2.txt").write_text("bb", encoding="utf-8")
    entries = build_inventory(tmp_path / "d")
    assert len(entries) == 2
    assert all(e.sha256 for e in entries)
    assert {e.size for e in entries} == {1, 2}
