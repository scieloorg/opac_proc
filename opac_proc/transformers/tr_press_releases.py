# coding: utf-8
import datetime

from opac_proc.datastore.models import (
    ExtractPressRelease,
    TransformPressRelease)
from opac_proc.transformers.base import BaseTransformer
from opac_proc.extractors.decorators import update_metadata

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "transform")
else:
    logger = getMongoLogger(__name__, "INFO", "transform")


class PressReleaseTransformer(BaseTransformer):
    extract_model_class = ExtractPressRelease
    extract_model_instance = None

    transform_model_class = TransformPressRelease
    transform_model_instance = None

    def get_extract_model_instance(self, id):
        return self.extract_model_class.objects.get(_id=id)

    def get_item_date(self):
        return datetime.datetime.strptime(self.extract_model_instance.published[5:25], '%d %b %Y %X')

    @update_metadata
    def transform(self):
        # aid
        uuid = self.extract_model_instance.uuid
        self.transform_model_instance['uuid'] = uuid
        self.transform_model_instance['aid'] = uuid
        self.transform_model_instance['published'] = self.get_item_date()

        return self.transform_model_instance
