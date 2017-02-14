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

        if feed.bozo == 1:
            self.error = 'Não é possível parsear o feed (%s)' % self.url
            self.log_error()

        return feed['items']

    def log_error(self):
        logger.error(self.error)
        raise Exception(self.error)

    @update_metadata
    def extract(self):
        """
        Conecta com a fonte (AM) e extrai todos os dados (coleção).
        """
        # logger.info(u'Inicia PressReleasesExtractor.extract(%s) %s' % (self.acronym, datetime.now()))

        raw_journal = self.get_items_from_feed()
        self._raw_data = dict(raw_journal)

        if not self._raw_data:
            return False
            self.error = u"Não foi possível recuperar o Press Release (url: %s, acronym: %s). A informação é vazía" % (
                self.url, self.acronym)
            self.log_error()

        logger.info(u"Fim PressReleasesExtractor.extract(%s) %s" % (
            self.acronym, datetime.now()))

    def save(self):
        """
        Salva os dados coletados no datastore (mongo)
        """
        logger.debug(u"Inciando metodo save()")

        if self.metadata['is_locked']:
            msg = u"atributos metadata['is_locked'] indica que o processamento não finalizou corretamente."
            logger.error(msg)
            raise Exception(msg)
        elif self.extract_model_class is None or self.extract_model_name is None:
            msg = u"atributos extract_model_class ou extract_model_name não forma definidos na subclasse"
            logger.error(msg)
            raise Exception(msg)
        elif self.metadata['process_start_at'] is None:
            msg = u"não foi definida o timestamp de inicio, você definiu/invocou o metodo: extract() na subclasse?"
            logger.error(msg)
            raise Exception(msg)
        # elif not self._raw_data:
        #     msg = u"os dados coletados estão vazios, você definiu/invocou o metodo: extract() na subclasse?"
        #     logger.error(msg)
        #     raise Exception(msg)
        elif not isinstance(self._raw_data, dict):
            msg = u"os dados extraidos, não são do tipo esperado: dict()"
            logger.error(msg)
            raise Exception(msg)
        else:
            # atualizamos as datas no self.metadata
            self.metadata['must_reprocess'] = False
            self._raw_data.update(**self.metadata)
            self.extract_model_instance = self.get_extract_model_instance()
            # salvamos no mongo
            try:
                if self.extract_model_instance:
                    logger.debug(u"extract_model_instance encontrado. Atualizando!")
                    self.extract_model_instance.modify(**self._raw_data)
                else:
                    logger.debug(u"extract_model_instance NÃO encontrado. Criando novo!")
                    self.extract_model_instance = self.extract_model_class(**self._raw_data)
                    self.extract_model_instance.save()
            except Exception, e:
                msg = u"Não foi possível salvar %s. Exceção: %s" % (
                    self.extract_model_name, e)
                logger.error(msg)
                raise e
            else:
                logger.debug(u"Reload de extract_model_instance")
                self.extract_model_instance.reload()
                logger.debug(u"Fim metodo save(), retornamos uuid: %s" % self.extract_model_instance.uuid)
                return self.extract_model_instance

