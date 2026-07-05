"""Extracteurs de contenu, sélectionnés par :class:`MediaType`.

Tous génériques : aucun ne connaît un fournisseur. Un extracteur transforme des
octets bruts en :class:`Document` (texte + métadonnées). Les médias binaires
(image, audio, vidéo, PDF non textuel) produisent un document « de référence »
sans texte, afin que le pipeline continue à créer un objet cognitif pointant
vers l'actif.
"""

from __future__ import annotations

import email
import json
from typing import Any, Callable, Dict, List

from scc_ingestion.core.models import Document, MediaType

# Signature d'un extracteur : (octets, métadonnées) -> Document.
Extractor = Callable[[bytes, Dict[str, Any]], Document]


def _decode(data: bytes) -> str:
    """Décode des octets en texte UTF-8 tolérant."""
    return data.decode("utf-8", errors="replace")


def extract_text(data: bytes, meta: Dict[str, Any]) -> Document:
    return Document(text=_decode(data), media_type=MediaType.TEXT, metadata=dict(meta))


def extract_markdown(data: bytes, meta: Dict[str, Any]) -> Document:
    return Document(text=_decode(data), media_type=MediaType.MARKDOWN, metadata=dict(meta))


def _flatten_json(value: Any, out: List[str]) -> None:
    """Collecte récursivement toutes les chaînes d'une structure JSON."""
    if isinstance(value, str):
        text = value.strip()
        if text:
            out.append(text)
    elif isinstance(value, dict):
        for key, val in value.items():
            _flatten_json(val, out)
    elif isinstance(value, list):
        for item in value:
            _flatten_json(item, out)


def extract_json(data: bytes, meta: Dict[str, Any]) -> Document:
    """Aplati un JSON générique en texte lisible (concaténation des chaînes)."""
    raw = _decode(data)
    metadata = dict(meta)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        # JSON Lines ou JSON invalide : on retombe sur le texte brut.
        metadata["json_parse"] = "fallback_text"
        return Document(text=raw, media_type=MediaType.JSON, metadata=metadata)
    parts: List[str] = []
    _flatten_json(parsed, parts)
    metadata["json_parse"] = "flattened"
    return Document(text="\n".join(parts), media_type=MediaType.JSON, metadata=metadata)


def extract_email(data: bytes, meta: Dict[str, Any]) -> Document:
    """Extrait sujet + corps texte d'un e-mail via la bibliothèque standard."""
    metadata = dict(meta)
    try:
        message = email.message_from_bytes(data)
    except Exception:  # noqa: BLE001 - repli défensif sur format inattendu
        return Document(text=_decode(data), media_type=MediaType.EMAIL, metadata=metadata)

    subject = message.get("subject", "")
    sender = message.get("from", "")
    metadata.update({"email_subject": subject, "email_from": sender})

    body_parts: List[str] = []
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    body_parts.append(payload.decode("utf-8", errors="replace"))
    else:
        payload = message.get_payload(decode=True)
        if payload:
            body_parts.append(payload.decode("utf-8", errors="replace"))

    text = "\n".join([p for p in [subject, sender, *body_parts] if p])
    return Document(text=text, media_type=MediaType.EMAIL, metadata=metadata)


def extract_reference(media_type: MediaType) -> Extractor:
    """Construit un extracteur « de référence » pour un média binaire.

    Ne tente pas de lire le contenu (nécessiterait une dépendance lourde) :
    produit un document sans texte, conservant les métadonnées. Le pipeline crée
    alors un objet cognitif catalogue pointant vers l'actif.
    """

    def _extract(data: bytes, meta: Dict[str, Any]) -> Document:
        metadata = dict(meta)
        metadata["byte_size"] = len(data)
        metadata["reference_only"] = True
        return Document(text="", media_type=media_type, metadata=metadata)

    return _extract


# Table de sélection par type de média.
_EXTRACTORS: Dict[MediaType, Extractor] = {
    MediaType.TEXT: extract_text,
    MediaType.CODE: extract_text,
    MediaType.MARKDOWN: extract_markdown,
    MediaType.JSON: extract_json,
    MediaType.EMAIL: extract_email,
}


def get_extractor(media_type: MediaType) -> Extractor:
    """Retourne l'extracteur adapté, avec repli « référence » pour les binaires."""
    return _EXTRACTORS.get(media_type, extract_reference(media_type))


__all__ = ["Extractor", "get_extractor", "extract_text", "extract_json", "extract_email"]
