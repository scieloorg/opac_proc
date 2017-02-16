# coding: utf-8
from datetime import datetime
from opac_proc.datastore.models import ExtractJournal
from opac_proc.extractors.base import BaseExtractor
from opac_proc.extractors.decorators import update_metadata

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "extract")
else:
    logger = getMongoLogger(__name__, "INFO", "extract")


class JournalExtractor(BaseExtractor):
    acronym = None
    issn = None

    extract_model_class = ExtractJournal

    def __init__(self, acronym, issn):
        super(JournalExtractor, self).__init__()
        self.acronym = acronym
        self.issn = issn
        self.get_instance_query = {
            'code': self.issn
        }

    @update_metadata
    def extract(self):
        """
        Conecta com a fonte (AM) e extrai todos os dados (coleção).
        """
        logger.info(u'Inicia JournalExtractor.extract(%s) %s' % (
            self.acronym, datetime.now()))

        journal = self.articlemeta.get_journal(collection=self.acronym, code=self.issn)
        self._raw_data = journal

        if not self._raw_data:
            msg = u"Não foi possível recuperar o Periódico (issn: %s, acronym: %s). A informação é vazía" % (
                self.issn, self.acronym)
            logger.error(msg)
            raise Exception(msg)

        logger.info(u'Fim JournalExtractor.extract(%s) %s' % (
            self.acronym, datetime.now()))
