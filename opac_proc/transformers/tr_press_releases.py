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

    def get_extract_model_instance(self, key):
        return self.extract_model_class.objects.get(uuid=key)

    def get_item_date(self):
        return datetime.datetime.strptime(
            self.extract_model_instance.published[5:25],
            '%d %b %Y %X')

    @update_metadata
    def transform(self):
        """
        Preparamos os dados para ser armazendos no modelo: Press Release
        https://github.com/scieloorg/opac_schema/blob/master/opac_schema/v1/models.py#L539

        _id -> <automatico>
        uuid -> self.extract_model_instance['uuid']
        journal -> self.extract_model_instance['journal_acronym']
        title -> self.extract_model_instance['title']
        language -> self.extract_model_instance['feed_lang']
        content -> self.extract_model_instance['summary']
        url -> self.extract_model_instance['url_id']
        publication_date -> self.extract_model_instance['published']
        created -> self.extract_model_instance['process_start_at']
        updated -> self.extract_model_instance['updated_at']
        """

        # UUID:
        self.transform_model_instance['uuid'] = self.extract_model_instance.uuid

        # JOURNAL:
        self.transform_model_instance['journal_acronym'] = self.extract_model_instance.journal_acronym

        # TITLE:
        self.transform_model_instance['title'] = self.extract_model_instance.title

        # LANGUAGE:
        self.transform_model_instance['language'] = self.extract_model_instance.feed_lang

        # CONTENT:
        self.transform_model_instance['content'] = self.extract_model_instance.summary

        # URL:
        self.transform_model_instance['url'] = self.extract_model_instance.url_id

        # PUBLICATION DATE:
        self.transform_model_instance['publication_date'] = self.get_item_date()

        # CREATED:
        self.transform_model_instance['created'] = datetime.datetime.now()

        # UPDATED:
        self.transform_model_instance['updated'] = datetime.datetime.now()

        return self.transform_model_instance
