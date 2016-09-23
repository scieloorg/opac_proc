# coding: utf-8
from opac_proc.datastore.models import (
    TransformCollection,
    LoadCollection)
from opac_proc.loaders.base import BaseLoader
from opac_schema.v1.models import Collection as OpacCollection


class CollectionLoader(BaseLoader):
    transform_model_class = TransformCollection
    transform_model_instance = None

    opac_model_class = OpacCollection
    opac_model_instance = None

    load_model_class = LoadCollection
    load_model_instance = None

    fields_to_load = [
        'acronym',
        'name',
    ]
