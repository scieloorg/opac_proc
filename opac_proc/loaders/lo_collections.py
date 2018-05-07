# coding: utf-8
from opac_proc.datastore.models import (
    TransformCollection,
    LoadCollection)
from opac_proc.loaders.base import BaseLoader
from opac_proc.datastore.identifiers_models import CollectionIdModel

from opac_schema.v1.models import Collection as OpacCollection
from opac_schema.v1.models import CollectionMetrics

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "load")
else:
    logger = getMongoLogger(__name__, "INFO", "load")


class CollectionLoader(BaseLoader):
    transform_model_class = TransformCollection
    transform_model_instance = None

    opac_model_class = OpacCollection
    opac_model_instance = None

    load_model_class = LoadCollection
    load_model_instance = None

    ids_model_class = CollectionIdModel
    ids_model_name = 'CollectionIdModel'
    ids_model_instance = None

    fields_to_load = [
        'acronym',
        'name',
        'metrics',
    ]

    def prepare_metrics(self):
        """
        metodo chamado na preparação dos dados a carregar no opac_schema
        deve retornar um valor válido para Collection.metrics
        """
        logger.debug(u"iniciando: prepare_metrics")
        if hasattr(self.transform_model_instance, 'metrics'):
            metrics_dict = self.transform_model_instance.metrics
            metrics_doc = CollectionMetrics(**metrics_dict)
        else:
            logger.info(u"Não existem 'metrics' transformados. uuid: %s" % self.transform_model_instance.uuid)

        logger.debug(u"metrics criadas: %s", metrics_dict)
        return metrics_doc
