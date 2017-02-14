# coding: utf-8
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

    extract_model_class = ExtractPressRelease

    def __init__(self, acronym, url):
        super(PressReleaseExtractor, self).__init__()
        self.acronym = acronym
        self.url = url
        self.get_instance_query = {
            'code': self.acronym
        }

    @update_metadata
    def extract(self):
        """
        Conecta com a fonte (AM) e extrai todos os dados (coleção).
        """
        logger.info(u'Inicia PressReleasesExtractor.extract(%s) %s' % (
            self.acronym, datetime.now()))

        # journal = self.articlemeta.get_journal(collection=self.acronym, code=self.issn)
        # self._raw_data = journal

        if not self._raw_data:
            msg = u"Não foi possível recuperar o Press Release (url: %s, acronym: %s). A informação é vazía" % (
                self.url, self.acronym)
            logger.error(msg)
            raise Exception(msg)

        logger.info(u'Fim PressReleasesExtractor.extract(%s) %s' % (
            self.acronym, datetime.now()))
