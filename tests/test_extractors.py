"""Tests des extracteurs de contenu."""

from __future__ import annotations

import json

from scc_ingestion.core.models import MediaType
from scc_ingestion.pipeline.extractors import get_extractor


def test_text_extractor():
    doc = get_extractor(MediaType.TEXT)(b"bonjour", {})
    assert doc.text == "bonjour"
    assert doc.media_type is MediaType.TEXT


def test_json_extractor_flattens_strings():
    payload = json.dumps({"a": "premier", "b": ["deuxième", {"c": "troisième"}], "n": 5})
    doc = get_extractor(MediaType.JSON)(payload.encode("utf-8"), {})
    assert "premier" in doc.text
    assert "deuxième" in doc.text
    assert "troisième" in doc.text
    assert doc.metadata["json_parse"] == "flattened"


def test_json_extractor_invalid_falls_back():
    doc = get_extractor(MediaType.JSON)(b"{not valid", {})
    assert doc.metadata["json_parse"] == "fallback_text"


def test_email_extractor_reads_subject_and_body():
    raw = (
        b"Subject: Test\r\n"
        b"From: a@b.c\r\n"
        b"Content-Type: text/plain\r\n\r\n"
        b"Corps du message"
    )
    doc = get_extractor(MediaType.EMAIL)(raw, {})
    assert "Test" in doc.text
    assert "Corps du message" in doc.text
    assert doc.metadata["email_subject"] == "Test"


def test_reference_extractor_for_binary():
    doc = get_extractor(MediaType.IMAGE)(b"\x89PNG\x00", {"filename": "x.png"})
    assert doc.text == ""
    assert doc.metadata["reference_only"] is True
    assert doc.metadata["byte_size"] == 5
