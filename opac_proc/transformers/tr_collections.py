# coding: utf-8
import logging
from datetime import datetime

from opac_proc.datastore.models import (
    ExtractCollection,
    TransformCollection)
from opac_proc.transformers.base import BaseTransformer
from opac_proc.extractors.decorators import update_metadata


logger = logging.getLogger(__name__)


class CollectionTransformer(BaseTransformer):
    extract_model_class = ExtractCollection
    extract_model_instance = None

    transform_model_class = TransformCollection
    transform_model_instance = None

    def get_extract_model_instance(self, key):
        # retornamos uma instancia de ExtractCollection
        # buscando pela key (=acronym)
        return self.extract_model_class.objects.get(acronym=key)

    @update_metadata
    def transform(self):
        self.transform_model_instance['uuid'] = self.extract_model_instance.uuid
        self.transform_model_instance['acronym'] = self.extract_model_instance.acronym
        self.transform_model_instance['name'] = self.extract_model_instance.name
        self.transform_model_instance['children_ids'] = self.extract_model_instance.children_ids
        return self.transform_model_instance
