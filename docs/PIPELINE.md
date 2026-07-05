# Le pipeline universel

Séquence **identique pour toutes les sources**, orchestrée par
`scc_ingestion.pipeline.pipeline.Pipeline`. Chaque étage est une classe `Stage`
qui lit et enrichit le `IngestionContext`.

```
intégrité → copie RAW → extraction → normalisation → découpage →
classification → objets cognitifs → indexation → rapport → archivage
```

## Contrat d'un étage

```python
class Stage(ABC):
    name: str
    def run(self, ctx: IngestionContext) -> None: ...
```

- En cas de **succès**, l'étage ajoute une vérification à `ctx.report`.
- En cas d'**échec fatal**, il lève une `IngestionError` : l'orchestrateur la
  capture, enregistre l'échec et (si `stop_on_error`) interrompt la suite.

## Les 10 étages

### 1. Intégrité — `stages/integrity.py`
Vérifie existence, type fichier, non-vacuité, puis calcule l'empreinte SHA-256.
Échoue (bloquant) si la source est introuvable, vide ou illisible.

### 2. Copie RAW — `stages/raw_copy.py`
Copie la source dans `queue/runs/<run_id>/raw/` **sans jamais la modifier**.
Recalcule/mémorise l'empreinte. Si la source est une **archive** (zip, tar,
tar.gz…), elle est décompressée dans `extracted/` (protection anti « zip slip »)
et la liste des fichiers extraits est mémorisée.

### 3. Extraction — `stages/extraction.py`
Sélectionne un **extracteur** selon le `MediaType` :

| Média | Extracteur | Résultat |
|-------|-----------|----------|
| texte, code | `extract_text` | texte décodé UTF-8 |
| markdown | `extract_markdown` | texte |
| JSON | `extract_json` | chaînes aplaties (générique, sans schéma) |
| e-mail | `extract_email` | sujet + expéditeur + corps (stdlib `email`) |
| image, audio, vidéo, PDF, document | `extract_reference` | document **de référence** (métadonnées, sans texte) |

### 4. Normalisation — `stages/normalization.py`
Uniformise l'encodage (NFC), les fins de ligne (`\n`), retire les espaces de fin
de ligne, réduit les lignes vides multiples et retire un BOM éventuel.

### 5. Découpage — `stages/chunking.py`
Découpe le texte normalisé en fragments de `max_chars` caractères avec
recouvrement `overlap` (paramétrable via `config.chunking`). Un actif binaire
sans texte produit **zéro fragment**.

### 6. Classification — `stages/classification.py`
Étiquetage **déterministe et piloté par la configuration** : catégorie issue du
connecteur, tags = source + type de média + tags de `classification_rules`
(mot-clé → tag). Aucune règle en dur propre à une source.

### 7. Objets cognitifs — `stages/cognitive.py`
Assemble document + fragments + classification en `CognitiveObject`. Un actif
binaire donne un objet « catalogue » pointant vers la source. En V1, un objet
par document.

### 8. Indexation — `stages/indexing.py`
Écrit chaque objet dans l'index global `queue/index.jsonl` (append-only) et
dépose une copie JSON par objet dans l'espace de travail de l'exécution.

### 9. Rapport — `stages/reporting.py`
Génère le rapport de l'exécution en **JSON** (machines) et **Markdown** (humains)
dans `reports/`.

### 10. Archivage — `stages/archiving.py`
Range la copie RAW dans `queue/_archive/<source>/<hash>_<nom>` — déduplication
naturelle par empreinte.

## Construire le pipeline

```python
from scc_ingestion.pipeline import build_default_pipeline
pipeline = build_default_pipeline(stop_on_error=True)
ctx = pipeline.run(context)
```

L'ordre et la composition sont librement modifiables : `Pipeline(stages=[...])`
accepte n'importe quelle liste de `Stage`. Voir [`EXTENSIONS.md`](EXTENSIONS.md).
