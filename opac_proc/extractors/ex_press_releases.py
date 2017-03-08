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
    lang = None
    url = None

    extract_model_class = ExtractPressRelease

    def __init__(self, acronym, url, lang):
        super(PressReleaseExtractor, self).__init__()
        self.acronym = acronym
        self.url = url
        self.lang = lang
        self.get_instance_query = {}

    def get_feed_entries(self):
        feed = feedparser.parse(self.url)
        if feed.bozo == 1:
            bozo_exception_msg = feed.bozo_exception.getMessage()
            msg = 'Não é possível parsear o feed (%s). Bozo exception message: %s' % (
                self.url, bozo_exception_msg)
            logger.error(msg)
            raise Exception(msg)
        else:
            return feed['entries']

    @update_metadata
    def extract(self, raw_entry):
        """
        Conecta com a fonte (RSS do blog: scielo press releases) e extrai todos os dados (press releases).
        """
        logger.info(u'Inicia PressReleasesExtractor.extract(%s) %s' % (self.acronym, datetime.now()))
        self.get_instance_query = {  # update query filter
            'url_id': raw_entry['id']
        }
        self._raw_data = raw_entry
        self._raw_data['url_id'] = raw_entry['id']
        del self._raw_data['id']
        del self._raw_data['published_parsed']
        # extra fields
        self._raw_data['journal_acronym'] = self.acronym
        self._raw_data['feed_lang'] = self.lang  # esperado: 'en' | 'es' | 'pt_BR'
        self._raw_data['feed_url_used'] = self.url

        if not self._raw_data:
            msg = u"Não foi possível recuperar o Press Release (url: %s, acronym: %s, lang: %s). A informação é vazía" % (self.url, self.acronym, self.lang)
            logger.error(msg)
            raise Exception(msg)

        logger.info(u"Fim PressReleasesExtractor.extract(%s) %s" % (
            self.acronym, datetime.now()))
