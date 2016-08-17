# coding: utf-8
import logging
from datetime import datetime

from opac_proc.datastore.extract.models import ExtractIssue
from opac_proc.extractors.base import BaseExtractor


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

    def extract(self):
        """
        Conecta com a fonte (AM) e extrai todos os dados (Issue).
        """
        super(IssueExtactor, self).extract()
        logger.info(u'Inicia IssueExtactor.extract(%s) %s' % (self.acronym, datetime.now()))
        self.extraction_start_time = datetime.now()

        issue = self.articlemeta.get_issue(collection=self.acronym, code=self.issue_id)
        self._raw_data = issue

        if not self._raw_data:
            msg = u"Não foi possível recuperar a Issue (acronym: %s). A informação é vazía" % self.acronym
            logger.error(msg)
            raise Exception(msg)

        logger.info(u'Fim IssueExtactor.extract(%s) %s' % (self.acronym, datetime.now()))
