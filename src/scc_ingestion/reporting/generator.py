"""Génération des rapports d'exécution (JSON + Markdown).

Un rapport résume une exécution du pipeline : source, empreinte, volumétrie et
liste des vérifications. Le JSON est destiné aux machines, le Markdown aux
humains. La date est injectable pour garantir des tests déterministes.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from scc_ingestion.pipeline.context import IngestionContext


def build_report_payload(ctx: IngestionContext, timestamp: Optional[str] = None) -> Dict[str, Any]:
    """Construit le dictionnaire de rapport à partir du contexte."""
    stamp = timestamp or datetime.now(timezone.utc).isoformat()
    return {
        "run_id": ctx.run_id,
        "timestamp": stamp,
        "source": ctx.source_item.source,
        "origin_uri": ctx.source_item.uri,
        "media_type": ctx.source_item.media_type.value,
        "sha256": ctx.metadata.get("sha256", ""),
        "aborted": ctx.aborted,
        "abort_reason": ctx.metadata.get("abort_reason", ""),
        "counts": {
            "chunks": len(ctx.chunks),
            "cognitive_objects": len(ctx.cognitive_objects),
            "extracted_files": len(ctx.extracted_files),
        },
        "cognitive_object_ids": [o.id for o in ctx.cognitive_objects],
        "report": ctx.report.to_dict(),
    }


def _render_markdown(payload: Dict[str, Any]) -> str:
    lines = [
        f"# Rapport d'ingestion — {payload['run_id']}",
        "",
        f"- **Horodatage** : {payload['timestamp']}",
        f"- **Source** : {payload['source']}",
        f"- **Origine** : {payload['origin_uri']}",
        f"- **Type de média** : {payload['media_type']}",
        f"- **SHA-256** : `{payload['sha256']}`",
        f"- **Statut** : {'❌ interrompu' if payload['aborted'] else '✅ complet'}",
        "",
        "## Volumétrie",
        f"- Fragments : {payload['counts']['chunks']}",
        f"- Objets cognitifs : {payload['counts']['cognitive_objects']}",
        f"- Fichiers extraits : {payload['counts']['extracted_files']}",
        "",
        "## Vérifications",
    ]
    for check in payload["report"]["checks"]:
        mark = "✅" if check["passed"] else "❌"
        detail = f" — {check['detail']}" if check["detail"] else ""
        lines.append(f"- {mark} {check['label']}{detail}")
    lines.append("")
    return "\n".join(lines)


def write_report(
    ctx: IngestionContext,
    reports_dir: Optional[Path] = None,
    timestamp: Optional[str] = None,
) -> Dict[str, Path]:
    """Écrit les rapports JSON et Markdown ; retourne leurs chemins."""
    target_dir = Path(reports_dir) if reports_dir else ctx.config.reports_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    payload = build_report_payload(ctx, timestamp=timestamp)
    json_path = target_dir / f"{ctx.run_id}.json"
    md_path = target_dir / f"{ctx.run_id}.md"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}


__all__ = ["build_report_payload", "write_report"]
