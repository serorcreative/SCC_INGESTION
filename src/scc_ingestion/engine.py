"""Façade du moteur d'ingestion.

Relie **connecteurs** et **pipeline** en une API unique et simple :

    engine = IngestionEngine()
    contexts = engine.ingest_path("/chemin/vers/export")

Le moteur reste agnostique : il choisit un connecteur (explicite ou auto-détecté),
lui demande de découvrir des :class:`SourceItem`, puis fait passer chacun dans le
pipeline universel.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Union

from scc_ingestion.connectors.base import Connector
from scc_ingestion.connectors.registry import ConnectorRegistry, default_registry
from scc_ingestion.core.config import IngestionConfig, load_config
from scc_ingestion.core.errors import ConnectorError
from scc_ingestion.core.media import detect_media_type
from scc_ingestion.core.models import SourceItem
from scc_ingestion.pipeline.context import IngestionContext
from scc_ingestion.pipeline.pipeline import Pipeline, build_default_pipeline


class IngestionEngine:
    """Point d'entrée programmatique du moteur."""

    def __init__(
        self,
        config: Optional[IngestionConfig] = None,
        registry: Optional[ConnectorRegistry] = None,
        pipeline: Optional[Pipeline] = None,
        stop_on_error: bool = True,
    ):
        self.config = config or load_config()
        self.config.ensure_directories()
        self.registry = registry or default_registry
        self.pipeline = pipeline or build_default_pipeline(stop_on_error=stop_on_error)

    # -- Sélection de connecteur ------------------------------------------------

    def resolve_connector(
        self, path: Union[str, Path], connector_name: Optional[str] = None
    ) -> Connector:
        """Retourne le connecteur explicite, ou l'auto-détecte par extension."""
        if connector_name:
            return self.registry.get(connector_name)
        found = self.registry.for_path(path)
        if found is None:
            raise ConnectorError(
                f"Aucun connecteur ne gère « {path} » ; précisez un connecteur."
            )
        return found

    # -- Exécutions -------------------------------------------------------------

    def ingest_item(self, item: SourceItem) -> IngestionContext:
        """Fait passer un unique :class:`SourceItem` dans le pipeline."""
        ctx = IngestionContext(source_item=item, config=self.config)
        return self.pipeline.run(ctx)

    def ingest_path(
        self, path: Union[str, Path], connector_name: Optional[str] = None
    ) -> List[IngestionContext]:
        """Découvre puis ingère tous les éléments trouvés sous ``path``."""
        connector = self.resolve_connector(path, connector_name)
        contexts: List[IngestionContext] = []
        for item in connector.discover(path):
            contexts.append(self.ingest_item(item))
        return contexts

    def ingest_file_as(
        self, path: Union[str, Path], source: str
    ) -> IngestionContext:
        """Ingère un fichier unique en lui imposant un nom de source arbitraire."""
        item = SourceItem(
            uri=str(path),
            source=source,
            media_type=detect_media_type(path),
            metadata={"filename": Path(path).name, "category": source},
        )
        return self.ingest_item(item)


__all__ = ["IngestionEngine"]
