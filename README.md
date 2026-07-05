# SCC — Moteur d'ingestion (`01_INGESTION`)

Moteur d'ingestion universel de **Seror Créative Core**. Il transforme des
sources hétérogènes (exports IA, dépôts, documents, médias, e-mails…) en
**objets cognitifs** normalisés, classés et indexés, via un pipeline unique et
générique.

> V1 — fondation complète, sans dépendance externe (bibliothèque standard
> Python uniquement). Extensible source par source.

## Installation

```bash
cd 01_INGESTION
python -m pip install -e ".[dev]"      # ou : export PYTHONPATH=src
```

## Utilisation en ligne de commande

```bash
scc-ingest connectors                  # liste les connecteurs disponibles
scc-ingest ingest <chemin>             # ingère un fichier ou un dossier (auto-détection)
scc-ingest ingest <dossier> --source chatgpt
scc-ingest watch ../02_RAW_SOURCES     # détecte (ponctuellement) les nouveaux fichiers
scc-ingest doctor                      # vérifie configuration et répertoires
```

Sans installation : `python -m scc_ingestion <commande>` (avec `PYTHONPATH=src`).

## Utilisation programmatique

```python
from scc_ingestion.engine import IngestionEngine

engine = IngestionEngine()
contexts = engine.ingest_path("chemin/vers/export", connector_name="claude")
for ctx in contexts:
    print(ctx.report.ok, len(ctx.cognitive_objects))
```

## Arborescence

```
01_INGESTION/
├── src/scc_ingestion/       # le moteur (package Python)
│   ├── core/                # modèles, config, rapport, erreurs, médias
│   ├── connectors/          # 12 connecteurs + interface + registre
│   ├── pipeline/            # orchestrateur + 10 étages + extracteurs
│   ├── validators/          # hash, intégrité, décompression, inventaire
│   ├── watchers/            # infrastructure de détection (V1 ponctuelle)
│   ├── reporting/           # génération des rapports
│   ├── engine.py            # façade connecteurs + pipeline
│   └── cli.py               # interface ligne de commande
├── config/                  # ingestion.json, sources.json
├── reports/  logs/  queue/  # sorties runtime (rapports, journaux, index, archive)
├── docs/                    # documentation détaillée
└── tests/                   # tests unitaires et d'intégration (pytest)
```

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — vue d'ensemble et principes.
- [`docs/LIFECYCLE.md`](docs/LIFECYCLE.md) — cycle de vie d'une source.
- [`docs/PIPELINE.md`](docs/PIPELINE.md) — les 10 étages en détail.
- [`docs/CONNECTORS.md`](docs/CONNECTORS.md) — l'interface et les 12 connecteurs.
- [`docs/EXTENSIONS.md`](docs/EXTENSIONS.md) — ajouter un connecteur, un étage, un extracteur.

## Tests

```bash
python -m pytest -q          # 59 tests, tous verts
```

## Principes

- **Générique** : aucun code spécifique à un fournisseur (ni ChatGPT ni autre).
- **Modulaire** : connecteurs, étages, extracteurs et watchers sont interchangeables.
- **Traçable** : empreinte SHA-256, copie RAW immuable, index append-only, rapports.
- **Sans dépendance** : repose sur la bibliothèque standard ; les couches lourdes
  (OCR, transcription, API distantes) se branchent via l'interface, sans hack.
