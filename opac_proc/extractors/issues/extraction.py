# coding: utf-8
import logging
from datetime import datetime

from opac_proc.datastore.extract.models import ExtractIssue
from opac_proc.extractors.base import BaseExtractor
from opac_proc.extractors.decorators import update_metadata


logger = logging.getLogger(__name__)


class IssueExtactor(BaseExtractor):
    acronym = None
    issue_id = None

    model_class = ExtractIssue
    model_name = 'ExtractIssue'

    def __init__(self, acronym, issue_id):
        super(IssueExtactor, self).__init__()
        self.acronym = acronym
        self.issue_id = issue_id

    @update_metadata
    def extract(self):
        """
        Conecta com a fonte (AM) e extrai todos os dados (Issue).
        """
        logger.info(u'Inicia IssueExtactor.extract(%s) %s' % (
            self.acronym, datetime.now()))

        issue = self.articlemeta.get_issue(collection=self.acronym, code=self.issue_id)
        self._raw_data = issue

        if not self._raw_data:
            msg = u"Não foi possível recuperar a Issue (acronym: %s). A informação é vazía" % self.acronym
            logger.error(msg)
            raise Exception(msg)

        logger.info(u'Fim IssueExtactor.extract(%s) %s' % (
            self.acronym, datetime.now()))
