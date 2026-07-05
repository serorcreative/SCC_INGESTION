# Connecteurs

Un connecteur est un **adaptateur** entre une source et le pipeline. Il ne fait
que deux choses : **découvrir** des unités et **récupérer** leur charge utile
brute. Toute interprétation est déléguée au pipeline — donc **aucune logique
propre à un fournisseur ne vit dans un connecteur**.

## Interface commune

`scc_ingestion.connectors.base.Connector` :

```python
class Connector(ABC):
    name: str                 # clé de registre
    category: str             # « ia », « document », « media », …
    media_types: tuple        # types revendiqués
    extensions: tuple         # extensions gérées (vide = toutes)
    remote: bool              # source distante (API) — informatif en V1
    auto_detect: bool         # éligible à l'auto-détection par extension

    def discover(self, source) -> Iterable[SourceItem]: ...
    def fetch(self, item: SourceItem) -> bytes: ...
    def supports(self, path) -> bool: ...
    def describe(self) -> dict: ...
```

`FileSystemConnector` fournit une implémentation générique sur le système de
fichiers : `discover` parcourt un répertoire en filtrant par extensions,
`fetch` lit les octets. **Tous les connecteurs V1 en héritent** et se contentent
de déclarer leur spécialité.

## Les 12 connecteurs V1

| Connecteur | Catégorie | Auto-détection | Extensions |
|------------|-----------|:--------------:|------------|
| `chatgpt` | ia | non¹ | json, jsonl, md, txt, html, zip |
| `claude` | ia | non¹ | json, jsonl, md, txt, html, zip |
| `github` | code | non¹ | toutes |
| `supabase` | database | non¹ | sql, json, jsonl, csv, ndjson |
| `base44` | app | non¹ | json, zip, js, ts, html, css, md |
| `documents` | document | oui | doc, docx, odt, rtf, xls, xlsx, ppt, pptx, txt |
| `pdf` | document | oui | pdf |
| `markdown` | document | oui | md, markdown |
| `images` | media | oui | png, jpg, jpeg, gif, webp, tif, tiff, bmp, svg |
| `audio` | media | oui | mp3, wav, flac, m4a, ogg |
| `video` | media | oui | mp4, mov, mkv, avi, webm |
| `emails` | communication | oui | eml, msg, olm, mbox |

¹ *Agrégateurs multi-formats : ils requièrent une sélection explicite
(`--source`) car plusieurs revendiquent les mêmes extensions.*

## Registre

`scc_ingestion.connectors.registry.ConnectorRegistry` :

```python
from scc_ingestion.connectors import default_registry

default_registry.available()               # noms disponibles
conn = default_registry.get("claude")       # instancier
default_registry.for_path("photo.png")      # auto-détecter (→ images)
default_registry.describe_all()             # métadonnées de tous
```

## État de la récupération distante

Les connecteurs marqués `remote = True` (chatgpt, claude, github, supabase,
base44) traitent en V1 leurs **exports locaux**. La récupération directe via API
se branchera par surcharge de `discover`/`fetch`, en passant les identifiants via
`options` — **sans modifier l'interface**. Voir [`EXTENSIONS.md`](EXTENSIONS.md).
