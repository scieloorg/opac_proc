# coding: utf-8
from opac_proc.datastore.models import (
    ExtractCollection,
    TransformCollection)
from opac_proc.datastore.identifiers_models import CollectionIdModel
from opac_proc.transformers.base import BaseTransformer
from opac_proc.extractors.decorators import update_metadata

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "transform")
else:
    logger = getMongoLogger(__name__, "INFO", "transform")


class CollectionTransformer(BaseTransformer):
    extract_model_class = ExtractCollection
    extract_model_instance = None

    transform_model_class = TransformCollection
    transform_model_instance = None

    ids_model_class = CollectionIdModel
    ids_model_instance = None

    def get_extract_model_instance(self, key):
        # retornamos uma instancia de ExtractCollection
        # buscando pela key (=acronym)
        logger.debug(u"CollectionTransformer: extraindo a e_collection com acronym: %s" % key)
        return self.extract_model_class.objects.get(acronym=key)

    @update_metadata
    def transform(self):
        logger.info(u'Inicia CollectionTransformer.transform')
        self.transform_model_instance['uuid'] = self.extract_model_instance.uuid
        self.transform_model_instance['acronym'] = self.extract_model_instance.acronym
        self.transform_model_instance['name'] = self.extract_model_instance.name
        self.transform_model_instance['metrics'] = self.extract_model_instance.metrics
        logger.info(u'Fim CollectionTransformer.transform')
        return self.transform_model_instance
