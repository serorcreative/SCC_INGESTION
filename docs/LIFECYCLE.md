# Cycle de vie d'une source

De l'arrivée d'un fichier à sa transformation en objets cognitifs indexés.

## Vue d'ensemble

```
  ┌─────────┐   ┌───────────┐   ┌────────────┐   ┌──────────────────┐   ┌──────────┐
  │ Arrivée │─► │ Détection │─► │ Connecteur │─► │ Pipeline (10 ét.) │─► │ Sorties  │
  │  RAW    │   │ (watcher) │   │ (discover) │   │                  │   │ + archive│
  └─────────┘   └───────────┘   └────────────┘   └──────────────────┘   └──────────┘
```

## 1. Arrivée dans `02_RAW_SOURCES`

Une source est déposée dans sa zone d'atterrissage (voir `config/sources.json`),
par exemple `02_RAW_SOURCES/01_CHATGPT/export.zip`.

## 2. Détection (watcher — infrastructure V1)

Un `FileSystemWatcher` compare l'état courant de l'arborescence à un instantané
précédent et liste les fichiers **apparus** ou **modifiés** :

```python
from scc_ingestion.watchers import FileSystemWatcher
events = FileSystemWatcher("02_RAW_SOURCES").scan()
```

> En V1, la détection est **ponctuelle** (appel explicite à `scan()`).
> L'automatisation (boucle, surveillance continue) est prévue en V2 et se
> branchera sur cette même méthode. Voir [`PIPELINE.md`](PIPELINE.md) et
> [`EXTENSIONS.md`](EXTENSIONS.md).

## 3. Sélection du connecteur

- **Explicite** : `--source claude` ou `ingest_path(path, connector_name="claude")`.
- **Auto-détection** : par extension, réservée aux connecteurs spécialisés
  (`markdown`, `pdf`, `images`…). Les agrégateurs multi-formats (`chatgpt`,
  `claude`, `github`, `supabase`, `base44`) exigent une sélection explicite.

Le connecteur **découvre** les `SourceItem` (`discover`) et sait **récupérer**
leur charge utile brute (`fetch`).

## 4. Traversée du pipeline

Chaque `SourceItem` devient un `IngestionContext` qui traverse les 10 étages
(détaillés dans [`PIPELINE.md`](PIPELINE.md)). Le contexte accumule : artefact
RAW, document, texte normalisé, fragments, classification, objets cognitifs et
rapport.

## 5. Sorties produites

| Sortie | Emplacement | Contenu |
|--------|-------------|---------|
| **Objets cognitifs** | `queue/runs/<run_id>/objects/*.json` | Unités de connaissance |
| **Index global** | `queue/index.jsonl` | Une ligne JSON par objet (append-only) |
| **Rapport** | `reports/<run_id>.json` + `.md` | Vérifications, volumétrie, empreinte |
| **Archive** | `queue/_archive/<source>/<hash>_<nom>` | Copie RAW dédupliquée |

## 6. Interruption et robustesse

Si un étage échoue, l'orchestrateur enregistre l'échec dans le rapport et
(par défaut) marque le contexte comme **interrompu** : les étages suivants sont
ignorés proprement. Le mode `--keep-going` désactive l'arrêt au premier échec.

## État du contexte au fil des étages

| Après l'étage | Champ renseigné |
|---------------|-----------------|
| intégrité | `metadata["sha256"]` |
| copie RAW | `raw_artifact`, éventuellement `extracted_files` |
| extraction | `document` |
| normalisation | `normalized_text` |
| découpage | `chunks` |
| classification | `classification` |
| objets cognitifs | `cognitive_objects` |
| indexation | `metadata["index_path"]` |
| rapport | `metadata["report_json"]`, `report_markdown` |
| archivage | `metadata["archive_path"]` |
