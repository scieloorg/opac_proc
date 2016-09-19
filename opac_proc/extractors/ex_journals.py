# coding: utf-8

import logging
from datetime import datetime

from opac_proc.datastore.models import ExtractJournal
from opac_proc.extractors.base import BaseExtractor
from opac_proc.extractors.decorators import update_metadata


logger = logging.getLogger(__name__)


class JournalExtactor(BaseExtractor):
    acronym = None
    issn = None

    extract_model_class = ExtractJournal

    def __init__(self, acronym, issn):
        super(JournalExtactor, self).__init__()
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
        logger.info(u'Inicia JournalExtactor.extract(%s) %s' % (
            self.acronym, datetime.now()))

        journal = self.articlemeta.get_journal(collection=self.acronym, code=self.issn)
        self._raw_data = journal

        if not self._raw_data:
            msg = u"Não foi possível recuperar o Periódico (issn: %s, acronym: %s). A informação é vazía" % (
                self.issn, self.acronym)
            logger.error(msg)
            raise Exception(msg)

        logger.info(u'Fim JournalExtactor.extract(%s) %s' % (
            self.acronym, datetime.now()))