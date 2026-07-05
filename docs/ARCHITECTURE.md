# Architecture du moteur d'ingestion SCC

## Objectif

Transformer **toute source** (export IA, dépôt de code, base de données,
document bureautique, PDF, image, audio, vidéo, e-mail…) en **objets cognitifs**
homogènes, exploitables par les couches supérieures de SCC (mémoire,
raisonnement, API).

## Principe directeur : un pipeline, plusieurs connecteurs

```
  ChatGPT ┐
  Claude  ┤
  GitHub  ┤
  …       ┤─►  Connecteur  ─►  ┌──────────────── PIPELINE UNIVERSEL ────────────────┐
  Images  ┤     (adaptateur)   │ intégrité → RAW → extraction → normalisation →     │
  E-mails ┘                    │ découpage → classification → objets cognitifs →    │
                               │ indexation → rapport → archivage                   │
                               └────────────────────────────────────────────────────┘
                                                     │
                                                     ▼
                                          Objets cognitifs + Index + Rapport
```

La **spécialisation** vit uniquement dans les connecteurs et la configuration.
Le pipeline, lui, est identique pour toutes les sources : c'est ce qui garantit
qu'aucune logique propre à un fournisseur ne se disperse dans le moteur.

## Couches

| Couche | Rôle | Module |
|--------|------|--------|
| **Core** | Modèles de données, configuration, rapport, erreurs, médias | `scc_ingestion.core` |
| **Connecteurs** | Découvrir et récupérer les sources (interface commune) | `scc_ingestion.connectors` |
| **Pipeline** | Chaîne de traitement universelle en 10 étages | `scc_ingestion.pipeline` |
| **Validators** | Hash, intégrité, décompression, inventaire | `scc_ingestion.validators` |
| **Watchers** | Détection des nouvelles sources (infrastructure V1) | `scc_ingestion.watchers` |
| **Reporting** | Rapports JSON + Markdown | `scc_ingestion.reporting` |
| **Façade** | API unique reliant connecteurs et pipeline | `scc_ingestion.engine` |
| **CLI** | Interface ligne de commande | `scc_ingestion.cli` |

## Modèles de données (le langage commun)

Défini dans `core/models.py`, tous neutres vis-à-vis de la source :

- **`SourceItem`** — unité découverte par un connecteur (avant traitement).
- **`RawArtifact`** — copie brute immuable + empreinte SHA-256.
- **`Document`** — contenu exploitable extrait.
- **`Chunk`** — fragment de document pour l'indexation.
- **`Classification`** — catégorie + tags.
- **`CognitiveObject`** — **la sortie de valeur** : unité de connaissance normalisée.

Le **`IngestionContext`** (`pipeline/context.py`) est l'enveloppe mutable qui
transporte cet état d'un étage à l'autre, avec le rapport cumulé.

## Décisions d'architecture

1. **Zéro dépendance obligatoire.** La V1 repose sur la bibliothèque standard.
   Les traitements lourds (OCR PDF, transcription audio, appels d'API distantes)
   se branchent via l'interface, sans imposer de dépendance au socle.
2. **Extraction par référence pour les binaires.** Images, audio, vidéo et PDF
   non textuels produisent un objet cognitif « catalogue » pointant vers l'actif,
   afin que rien ne soit perdu et que l'enrichissement soit incrémental.
3. **Isolation des étages.** Chaque étage lit/enrichit le contexte et signale
   son résultat ; une exception est capturée par l'orchestrateur, transformée en
   échec de rapport, sans faire tomber le processus.
4. **Traçabilité de bout en bout.** SHA-256 sur la source et la copie RAW, index
   JSONL append-only, archive dédupliquée par empreinte, rapport par exécution.

## Voir aussi

- Cycle de vie détaillé → [`LIFECYCLE.md`](LIFECYCLE.md)
- Étages du pipeline → [`PIPELINE.md`](PIPELINE.md)
- Connecteurs → [`CONNECTORS.md`](CONNECTORS.md)
- Étendre le moteur → [`EXTENSIONS.md`](EXTENSIONS.md)
