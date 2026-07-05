# Étendre le moteur

Le moteur est conçu pour grandir **par ajout**, sans toucher au socle. Trois
points d'extension : connecteurs, étages, extracteurs. Plus les watchers.

## Ajouter un connecteur

1. Créer `connectors/mon_connecteur.py` :

```python
from scc_ingestion.connectors.base import FileSystemConnector
from scc_ingestion.core.models import MediaType

class NotionConnector(FileSystemConnector):
    name = "notion"
    category = "document"
    media_types = (MediaType.MARKDOWN, MediaType.JSON)
    extensions = (".md", ".json")
    remote = True
    auto_detect = False   # export multi-format
```

2. L'enregistrer :

```python
from scc_ingestion.connectors import default_registry
default_registry.register(NotionConnector)
```

Pour un connecteur **distant** (API), surchargez `discover` et `fetch` en lisant
les identifiants dans `self.options` — l'interface reste inchangée :

```python
class SupabaseApiConnector(SupabaseConnector):
    def discover(self, source):
        client = connect(self.options["url"], self.options["key"])
        for row in client.query(source):
            yield SourceItem(uri=row["id"], source=self.name, ...)
    def fetch(self, item):
        return serialize(...)
```

## Ajouter un étage de pipeline

1. Créer une sous-classe de `Stage` :

```python
from scc_ingestion.pipeline.stage import Stage
from scc_ingestion.pipeline.context import IngestionContext

class EmbeddingStage(Stage):
    name = "embeddings"
    def run(self, ctx: IngestionContext) -> None:
        for chunk in ctx.chunks:
            chunk.metadata["vector_dim"] = 1536   # calcul réel ici
        self._ok(ctx, f"{len(ctx.chunks)} fragment(s) vectorisé(s)")
```

2. L'insérer dans le pipeline :

```python
from scc_ingestion.pipeline import Pipeline, build_default_pipeline
base = build_default_pipeline()
stages = base.stages[:6] + [EmbeddingStage()] + base.stages[6:]
pipeline = Pipeline(stages)
```

## Ajouter un extracteur

Pour prendre en charge un nouveau média (ex. OCR de PDF, transcription audio),
enregistrez une fonction `(bytes, meta) -> Document` :

```python
from scc_ingestion.pipeline import extractors
from scc_ingestion.core.models import Document, MediaType

def extract_pdf(data, meta):
    text = run_ocr(data)                     # dépendance optionnelle
    return Document(text=text, media_type=MediaType.PDF, metadata=dict(meta))

extractors._EXTRACTORS[MediaType.PDF] = extract_pdf
```

> Les dépendances lourdes (OCR, ASR) restent **optionnelles** : elles ne sont
> chargées que par l'extracteur qui les utilise, préservant le socle sans
> dépendance.

## Ajouter / brancher un watcher

L'infrastructure V1 est ponctuelle (`FileSystemWatcher.scan()`). Pour
l'**automatisation V2**, brancher `scan()` sur une boucle ou une planification :

```python
from scc_ingestion.watchers import FileSystemWatcher
from scc_ingestion.engine import IngestionEngine

watcher = FileSystemWatcher("02_RAW_SOURCES")
engine = IngestionEngine()

def tick():                       # appelé par un planificateur externe
    for event in watcher.scan():
        engine.ingest_path(event.path)
```

Un watcher personnalisé implémente simplement l'interface `Watcher`
(`scan`, et plus tard `start`/`stop`).

## Règles de classification

Ajoutez des tags sans coder : éditez `classification_rules` dans
`config/ingestion.json` (`"tag": ["mot-clé", …]`). Aucune recompilation.

## Principes à respecter

- **Rien de spécifique à un fournisseur dans le socle.** La spécialisation vit
  dans un connecteur ou un extracteur dédié.
- **Dépendances optionnelles**, jamais imposées au cœur.
- **Un étage = une responsabilité**, testable isolément.
