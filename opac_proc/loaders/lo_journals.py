# coding: utf-8
import datetime
from mongoengine import DoesNotExist
from mongoengine.context_managers import switch_db
from opac_proc.datastore.mongodb_connector import get_opac_webapp_db_name
from opac_proc.loaders.base import BaseLoader
from opac_proc.datastore.models import (
    TransformJournal,
    TransformIssue,
    LoadJournal)
from opac_schema.v1.models import Journal as OpacJournal
from opac_schema.v1.models import (
    Collection,
    Timeline,
    Mission,
    OtherTitle,
    LastIssue,
    JounalMetrics)

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "load")
else:
    logger = getMongoLogger(__name__, "INFO", "load")

OPAC_WEBAPP_DB_NAME = get_opac_webapp_db_name()


class JournalLoader(BaseLoader):
    transform_model_class = TransformJournal
    transform_model_instance = None

    opac_model_class = OpacJournal
    opac_model_instance = None

    load_model_class = LoadJournal
    load_model_instance = None

    fields_to_load = [
        'jid',
        'collection',
        'timeline',
        'subject_categories',
        'study_areas',
        'social_networks',
        'title',
        'title_iso',
        'short_title',
        'title_slug',
        'created',
        'updated',
        'acronym',
        'scielo_issn',
        'print_issn',
        'eletronic_issn',
        'subject_descriptors',
        'copyrighter',
        'online_submission_url',
        'logo_url',
        'previous_journal_ref',
        'other_titles',
        'publisher_name',
        'publisher_country',
        'publisher_state',
        'publisher_city',
        'publisher_address',
        'publisher_telephone',
        'current_status',
        'mission',
        'index_at',
        'sponsors',
        'issue_count',
        'last_issue',
        'metrics',
    ]

    def prepare_collection(self):
        """
        metodo chamado na preparação dos dados a carregar no opac_schema
        deve retornar um valor válido para Journal.collection
        """
        logger.debug(u"iniciando: prepare_collection")
        transformed_coll_uuid_str = str(self.transform_model_instance.collection).replace("-", "")

        try:
            with switch_db(Collection, OPAC_WEBAPP_DB_NAME) as OPAC_Collection:
                opac_collection = OPAC_Collection.objects.get(_id=transformed_coll_uuid_str)
                return opac_collection
        except DoesNotExist, e:
            logger.error(
                u"collection (_id: %s) não encontrada. Já fez o Load Collection?",
                transformed_coll_uuid_str)
            raise e

    def prepare_timeline(self):
        """
        metodo chamado na preparação dos dados a carregar no opac_schema
        deve retornar um valor válido para Journal.collection do
        """
        logger.debug(u"iniciando: prepare_timeline")
        timeline_docs = []
        if hasattr(self.transform_model_instance, 'timeline'):
            for tl_dict in self.transform_model_instance.timeline:
                timeline_doc = Timeline(**tl_dict)
                timeline_docs.append(timeline_doc)
        else:
            logger.info(u"Não existem Timelines transformados. uuid: %s" % self.transform_model_instance.uuid)

        logger.debug(u"timeline criadas: %s" % len(timeline_docs))
        return timeline_docs

    def prepare_social_networks(self):
        """
        metodo chamado na preparação dos dados a carregar no opac_schema
        deve retornar um valor válido para Journal.collection do
        """
        # ainda não processmos esta infomação desde o AM/Xylose/Extract
        logger.debug(u"iniciando: prepare_social_networks")
        return []

    def prepare_other_titles(self):
        """
        metodo chamado na preparação dos dados a carregar no opac_schema
        deve retornar um valor válido para Journal.collection do
        """
        logger.debug(u"iniciando: prepare_other_titles")
        other_titles_docs = []
        if hasattr(self.transform_model_instance, 'other_titles'):
            for otitle_dict in self.transform_model_instance.other_titles:
                other_titles_doc = OtherTitle(**otitle_dict)
                other_titles_docs.append(other_titles_doc)
        else:
            logger.info(u"Não existem Other Titles transformados. uuid: %s" % self.transform_model_instance.uuid)

        logger.debug(u"other_titles criados: %s" % len(other_titles_docs))
        return other_titles_docs

    def prepare_mission(self):
        """
        metodo chamado na preparação dos dados a carregar no opac_schema
        deve retornar um valor válido para Journal.collection do
        """
        logger.debug(u"iniciando: prepare_mission")
        mission_docs = []
        if hasattr(self.transform_model_instance, 'mission'):
            for mission_dict in self.transform_model_instance.mission:
                mission_doc = Mission(**mission_dict)
                mission_docs.append(mission_doc)
        else:
            logger.info(u"Não existem Missions transformados. uuid: %s" % self.transform_model_instance.uuid)

        logger.debug(u"Missions criados: %s" % len(mission_docs))
        return mission_docs

    def prepare_last_issue(self):
        """
        metodo chamado na preparação dos dados a carregar no opac_schema
        deve retornar um valor válido para Journal.collection do
        """
        logger.debug(u"iniciando: prepare_last_issue")
        t_journal_uuid = self.transform_model_instance.uuid
        t_issue = TransformIssue.objects.filter(
            journal=t_journal_uuid).order_by('-year', '-order').first().select_related()

        logger.debug(u"last issue: t_issue encontrado (iid: %s)" % t_issue.iid)
        last_issue_sections = []
        if hasattr(t_issue, 'sections'):
            last_issue_sections = t_issue.sections
        else:
            logger.info(u"Não existem Issue.sections transformados. uuid: %s" % t_issue.uuid)

        last_issue_data = {
            'iid': str(t_issue.uuid).replace("-", ""),
            'sections': last_issue_sections,
        }

        if hasattr(t_issue, 'volume'):
            last_issue_data['volume'] = t_issue.volume

        if hasattr(t_issue, 'number'):
            last_issue_data['number'] = t_issue.number

        if hasattr(t_issue, 'start_month'):
            last_issue_data['start_month'] = t_issue.start_month

        if hasattr(t_issue, 'end_month'):
            last_issue_data['end_month'] = t_issue.end_month

        if hasattr(t_issue, 'label'):
            last_issue_data['label'] = t_issue.label

        if hasattr(t_issue, 'year'):
            last_issue_data['year'] = t_issue.year

        logger.debug(u"criando documento LastIssue: %s" % last_issue_data)
        return LastIssue(**last_issue_data)

    def prepare_issue_count(self):
        logger.debug(u"iniciando: prepare_issue_count")
        issue_count = TransformIssue.objects.filter(journal=self.transform_model_instance).count()
        logger.debug(u"Quantidade de issues encontradas: %s" % issue_count)
        return issue_count

    def prepare_metrics(self):
        """
        metodo chamado na preparação dos dados a carregar no opac_schema
        deve retornar um valor válido para Journal.metrics
        """
        logger.debug(u"iniciando: prepare_metrics")
        if hasattr(self.transform_model_instance, 'metrics'):
            metrics_dict = self.transform_model_instance.metrics
            metrics_doc = JounalMetrics(**metrics_dict)
        else:
            logger.info(u"Não existem 'metrics' transformados. uuid: %s" % self.transform_model_instance.uuid)

        logger.debug(u"metrics criadas: %s", metrics_dict)
        return metrics_doc
