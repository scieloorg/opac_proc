# coding: utf-8
from datetime import datetime
from opac_proc.datastore.models import ExtractIssue
from opac_proc.datastore.identifiers_models import IssueIdModel
from opac_proc.extractors.base import BaseExtractor
from opac_proc.extractors.decorators import update_metadata

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "extract")
else:
    logger = getMongoLogger(__name__, "INFO", "extract")


class IssueExtractor(BaseExtractor):
    issue_pid = None

    extract_model_class = ExtractIssue
    ids_model_class = IssueIdModel
    ids_model_name = 'IssueIdModel'

    def __init__(self, issue_pid):
        super(IssueExtractor, self).__init__()
        self.acronym = config.OPAC_PROC_COLLECTION
        self.issue_pid = issue_pid
        self.get_instance_query = {
            'collection': self.acronym,
            'code': self.issue_pid,
        }
        self.get_identifier_query = {
            'issue_pid': self.issue_pid
        }

    @update_metadata
    def extract(self):
        """
        Conecta com a fonte (AM) e extrai todos os dados (Issue).
        """
        logger.info(u'Inicia IssueExtactor.extract(%s) %s' % (
            self.acronym, datetime.now()))

        issue = self.articlemeta.get_issue(collection=self.acronym, code=self.issue_pid)
        self._raw_data = issue

        if not self._raw_data:
            msg = u"Não foi possível recuperar a Issue (acronym: %s). A informação é vazía" % self.acronym
            logger.error(msg)
            raise Exception(msg)

        logger.info(u'Fim IssueExtactor.extract(%s) %s' % (
            self.acronym, datetime.now()))
