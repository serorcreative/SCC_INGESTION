"""SCC Ingestion — moteur d'ingestion universel de Seror Créative Core.

Le moteur transforme une *source hétérogène* (export ChatGPT, dépôt GitHub,
document PDF, image, e-mail…) en *objets cognitifs* normalisés, classés et
indexés, à travers un pipeline unique et générique.

Architecture en trois couches :

* ``connectors`` — adaptateurs par source ; tous exposent la même interface
  :class:`~scc_ingestion.connectors.base.Connector`.
* ``pipeline``   — chaîne de traitement universelle (intégrité → RAW → extraction
  → normalisation → découpage → classification → objets cognitifs → indexation
  → rapport → archivage).
* ``validators`` / ``watchers`` / ``reporting`` — services transverses.

Aucun connecteur ne contient de logique spécifique à un fournisseur : toute la
spécialisation passe par la configuration et l'interface commune.
"""

from __future__ import annotations

__version__ = "1.0.0"

__all__ = ["__version__"]
