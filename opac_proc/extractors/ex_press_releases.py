# coding: utf-8
import json

import feedparser

from datetime import datetime
from opac_proc.datastore.models import ExtractPressRelease
from opac_proc.extractors.base import BaseExtractor
from opac_proc.extractors.decorators import update_metadata

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "extract")
else:
    logger = getMongoLogger(__name__, "INFO", "extract")


class PressReleaseExtractor(BaseExtractor):
    acronym = None
    url = None
    error = None
    is_empty = True

    extract_model_class = ExtractPressRelease

    def __init__(self, acronym, url):
        super(PressReleaseExtractor, self).__init__()
        self.acronym = acronym
        self.url = url
        self.get_instance_query = {
            'code': self.acronym
        }

    def get_items_from_feed(self):
        feed = feedparser.parse(self.url)
        items = feed['items']

        if feed.bozo == 1:
            self.error = 'Não é possível parsear o feed (%s)' % self.url
            self.log_error()

        if len(items) > 0:
            self.is_empty = False
            self._raw_data = dict(items)

    def log_error(self):
        logger.error(self.error)
        raise Exception(self.error)

    @update_metadata
    def extract(self):
        """
        Conecta com a fonte (AM) e extrai todos os dados (coleção).
        """
        logger.info(u'Inicia PressReleasesExtractor.extract(%s) %s' % (self.acronym, datetime.now()))

        if not self._raw_data:
            self.error = u"Não foi possível recuperar o Press Release (url: %s, acronym: %s). A informação é vazía" % (
                self.url, self.acronym)
            self.log_error()

        logger.info(u"Fim PressReleasesExtractor.extract(%s) %s" % (
            self.acronym, datetime.now()))

