# coding: utf-8
import logging

from opac_proc.loaders.base import BaseLoader
from opac_proc.datastore.transform.models import TransformCollection
from opac_schema.v1.models import Collection as OpacCollection

logger = logging.getLogger(__name__)


class CollectionLoader(BaseLoader):
    transform_model_class = TransformCollection
    transform_model_name = 'TransformCollection'
    transform_model_instance = None

    opac_model_class = OpacCollection
    opac_model_name = 'OpacCollection'
    opac_model_instance = None

    fields_to_load = [
        'acronym',
        'name',
    ]
