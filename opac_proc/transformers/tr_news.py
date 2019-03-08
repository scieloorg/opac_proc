# coding: utf-8
import datetime

from opac_proc.datastore.models import (
    ExtractNews,
    TransformNews)
from opac_proc.transformers.base import BaseTransformer
from opac_proc.extractors.decorators import update_metadata

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "transform")
else:
    logger = getMongoLogger(__name__, "INFO", "transform")


class NewsTransformer(BaseTransformer):
    extract_model_class = ExtractNews
    extract_model_instance = None

    transform_model_class = TransformNews
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
        Preparamos os dados para ser armazendos no modelo: News
        https://github.com/scieloorg/opac_schema/blob/master/opac_schema/v1/models.py#L30

        _id -> <automatico>
        uuid -> self.extract_model_instance['uuid']
        url -> self.extract_model_instance['url_id']
        publication_date -> self.extract_model_instance['published']
        title -> self.extract_model_instance['title']
        description -> self.extract_model_instance['summary']
        language -> self.extract_model_instance['feed_lang']
        image_url -> self.extract_model_instance['media_content'][0]['url']
        """

        # UUID:
        self.transform_model_instance['uuid'] = self.extract_model_instance.uuid

        # URL:
        self.transform_model_instance['url'] = self.extract_model_instance.url_id

        # PUBLICATION DATE:
        self.transform_model_instance['publication_date'] = self.get_item_date()

        # TITLE:
        self.transform_model_instance['title'] = self.extract_model_instance.title

        # DESCRIPTION:
        self.transform_model_instance['description'] = self.extract_model_instance.summary

        # LANGUAGE:
        self.transform_model_instance['language'] = self.extract_model_instance.feed_lang

        # MEDIA CONTENT:
        if hasattr(self.extract_model_instance, 'media_content'):
            media_content = self.extract_model_instance.media_content
            if len(media_content) > 0 and media_content[0].get('url'):
                self.transform_model_instance['image_url'] = media_content[0]['url']

        return self.transform_model_instance
