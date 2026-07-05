"""Interface en ligne de commande du moteur d'ingestion.

Basée sur ``argparse`` (bibliothèque standard) pour rester sans dépendance.

Commandes :

* ``connectors``       — liste les connecteurs disponibles ;
* ``ingest <chemin>``  — exécute le pipeline sur un fichier ou un dossier ;
* ``watch <racine>``   — détecte (ponctuellement) les nouveaux fichiers ;
* ``doctor``           — vérifie la configuration et les répertoires ;
* ``version``          — affiche la version du moteur.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from scc_ingestion import __version__
from scc_ingestion.connectors.registry import default_registry
from scc_ingestion.core.config import load_config
from scc_ingestion.core.errors import IngestionError
from scc_ingestion.engine import IngestionEngine
from scc_ingestion.watchers.filesystem import FileSystemWatcher


def _cmd_connectors(_: argparse.Namespace) -> int:
    print("Connecteurs disponibles :")
    for desc in default_registry.describe_all():
        remote = "distant" if desc["remote"] else "local"
        exts = ", ".join(desc["extensions"]) or "toutes extensions"
        print(f"  • {desc['name']:<10} [{desc['category']}, {remote}] — {exts}")
    return 0


def _cmd_ingest(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config)) if args.config else load_config()
    engine = IngestionEngine(config=config, stop_on_error=not args.keep_going)
    try:
        contexts = engine.ingest_path(args.path, connector_name=args.source)
    except IngestionError as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 2

    if not contexts:
        print("Aucun élément ingéré (aucune source compatible trouvée).")
        return 0

    ok = 0
    for ctx in contexts:
        status = "OK " if ctx.report.ok and not ctx.aborted else "ÉCHEC"
        ok += 1 if ctx.report.ok and not ctx.aborted else 0
        print(
            f"  [{status}] {ctx.source_item.metadata.get('filename', ctx.source_item.uri)} "
            f"— {len(ctx.cognitive_objects)} objet(s), run {ctx.run_id}"
        )
    print(f"\n{ok}/{len(contexts)} source(s) ingérée(s) avec succès.")
    return 0 if ok == len(contexts) else 1


def _cmd_watch(args: argparse.Namespace) -> int:
    watcher = FileSystemWatcher(args.root)
    events = watcher.scan(persist=not args.dry_run)
    if not events:
        print("Aucune nouveauté détectée.")
        return 0
    print(f"{len(events)} nouveauté(s) détectée(s) :")
    for event in events:
        print(f"  • [{event.kind}] {event.path}")
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config)) if args.config else load_config()
    print(f"Moteur d'ingestion SCC v{__version__}")
    print(f"  racine moteur   : {config.engine_root}")
    print(f"  sources RAW     : {config.raw_sources_root}")
    print(f"  espace de travail: {config.work_root}")
    print(f"  rapports        : {config.reports_dir}")
    print(f"  index           : {config.index_path}")
    config.ensure_directories()
    print(f"  connecteurs     : {len(default_registry.available())}")
    print("  répertoires runtime : OK")
    return 0


def _cmd_version(_: argparse.Namespace) -> int:
    print(__version__)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scc-ingest",
        description="Moteur d'ingestion universel de Seror Créative Core.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_conn = sub.add_parser("connectors", help="liste les connecteurs disponibles")
    p_conn.set_defaults(func=_cmd_connectors)

    p_ing = sub.add_parser("ingest", help="ingère un fichier ou un dossier")
    p_ing.add_argument("path", help="chemin du fichier ou dossier à ingérer")
    p_ing.add_argument("--source", help="nom du connecteur à forcer (sinon auto-détection)")
    p_ing.add_argument("--config", help="chemin d'un fichier de configuration JSON")
    p_ing.add_argument(
        "--keep-going",
        action="store_true",
        help="ne pas interrompre le pipeline au premier échec d'étage",
    )
    p_ing.set_defaults(func=_cmd_ingest)

    p_watch = sub.add_parser("watch", help="détecte les nouveaux fichiers (ponctuel)")
    p_watch.add_argument("root", help="racine à surveiller (ex. 02_RAW_SOURCES)")
    p_watch.add_argument(
        "--dry-run",
        action="store_true",
        help="ne pas mémoriser l'état (détection répétable)",
    )
    p_watch.set_defaults(func=_cmd_watch)

    p_doctor = sub.add_parser("doctor", help="vérifie configuration et répertoires")
    p_doctor.add_argument("--config", help="chemin d'un fichier de configuration JSON")
    p_doctor.set_defaults(func=_cmd_doctor)

    p_ver = sub.add_parser("version", help="affiche la version")
    p_ver.set_defaults(func=_cmd_version)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
