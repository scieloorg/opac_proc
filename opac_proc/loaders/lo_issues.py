# coding: utf-8
from mongoengine.context_managers import switch_db
from mongoengine import DoesNotExist

from opac_proc.datastore.mongodb_connector import get_opac_webapp_db_name
from opac_proc.loaders.base import BaseLoader
from opac_proc.datastore.models import (
    TransformArticle,
    TransformIssue,
    LoadIssue)
from opac_schema.v1.models import Issue as OpacIssue
from opac_schema.v1.models import Journal as OpacJournal

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "load")
else:
    logger = getMongoLogger(__name__, "INFO", "load")

OPAC_WEBAPP_DB_NAME = get_opac_webapp_db_name()


class IssueLoader(BaseLoader):
    transform_model_class = TransformIssue
    transform_model_instance = None

    opac_model_class = OpacIssue
    opac_model_instance = None

    load_model_class = LoadIssue
    load_model_instance = None

    fields_to_load = [
        'iid',
        'created',
        'updated',
        'journal',
        'volume',
        'number',
        'type',
        'start_month',
        'end_month',
        'year',
        'label',
        'order',
        'pid',
        'suppl_text',
    ]

    def prepare_journal(self):
        logger.debug(u"iniciando prepare_journal")
        t_journal_uuid = self.transform_model_instance.journal
        t_journal_uuid_str = str(t_journal_uuid).replace("-", "")

        with switch_db(OpacJournal, OPAC_WEBAPP_DB_NAME):
            try:
                opac_journal = OpacJournal.objects.get(_id=t_journal_uuid_str)
                logger.debug(u"Journal: %s (_id: %s) encontrado" % (opac_journal.acronym, t_journal_uuid_str))
            except DoesNotExist, e:
                logger.error(u"Journal (_id: %s) não encontrado. Já fez o Load Journal?" % t_journal_uuid_str)
                raise e
        return opac_journal

    def prepare_type(self):
        logger.debug(u"iniciando prepare_type")
        if self.transform_model_instance['type'] == 'outdated_ahead':
            # se o transformado já foi marcado como 'outdated_ahead'
            # não precisamos fazer nada
            return self.transform_model_instance['type']
        else:
            t_journal_uuid = self.transform_model_instance.journal
            ahead_transformed_issues = self.transform_model_class.objects.filter(
                type='ahead', journal=t_journal_uuid).order_by('-year', '-order')

            if ahead_transformed_issues:
                # se tem algum issue to typo ahead, separamos o primeiro do resto
                ahead_transformed_issue = ahead_transformed_issues.first()
                outdated_ahead_transformed_issues = ahead_transformed_issues.filter(
                    uuid__ne=ahead_transformed_issue.uuid)
                # alteramos o tipo dos velhos para: 'outdated_ahead'
                # outdated_ahead_transformed_issues.modify(upsert=True, **{'type': 'outdated_ahead'})
                for tr_issue in outdated_ahead_transformed_issues:
                    tr_issue['type'] = 'outdated_ahead'
                    tr_issue.save()

                # se houver artigos associados ao "ahead_transformed_issue" deixo o type: 'ahead'
                # caso contario, renomeia o type para 'outdated_ahead'
                count_transformed_articles_of_ahead = TransformArticle.objects.filter(
                    issue=ahead_transformed_issue.uuid).count()

                if count_transformed_articles_of_ahead == 0:
                    logger.debug(u"retorno do prepare_type: para o issue com uuid: %s o tipo: 'outdated_ahead'" %
                                 self.transform_model_instance.uuid)
                    return 'outdated_ahead'
                else:
                    return self.transform_model_instance['type']
            else:
                return self.transform_model_instance['type']

    def prepare_suppl_text(self):
        logger.debug(u"iniciando prepare_suppl_text")
        t_issue = self.transform_model_instance
        if hasattr(t_issue, 'supplement_number') or \
           hasattr(t_issue, 'supplement_volume'):
            return t_issue.supplement_number or t_issue.supplement_volume
        else:
            return u''
