# coding: utf-8

from opac_proc.datastore.mongodb_connector import get_opac_webapp_db_name
from opac_proc.loaders.base import BaseLoader
from opac_proc.datastore.models import (
    LoadNews,
    TransformNews)
from opac_proc.datastore.identifiers_models import NewsIdModel

from opac_schema.v1.models import News as OpacNews


from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "load")
else:
    logger = getMongoLogger(__name__, "INFO", "load")

OPAC_WEBAPP_DB_NAME = get_opac_webapp_db_name()


class NewsLoader(BaseLoader):
    transform_model_class = TransformNews
    transform_model_instance = None

    opac_model_class = OpacNews
    opac_model_instance = None

    load_model_class = LoadNews
    load_model_instance = None

    ids_model_class = NewsIdModel
    ids_model_name = 'NewsIdModel'
    ids_model_instance = None

    fields_to_load = [
        'url',
        'publication_date',
        'title',
        'description',
        'language',
        'image_url',
    ]
