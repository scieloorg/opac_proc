# coding: utf-8
import logging

from mongoengine.context_managers import switch_db

from opac_proc.datastore.mongodb_connector import get_opac_webapp_db_name
from opac_proc.loaders.base import BaseLoader
from opac_proc.datastore.transform.models import TransformCollection, TransformJournal, TransformIssue
from opac_schema.v1.models import Issue as OpacIssue
from opac_schema.v1.models import Journal as OpacJournal


logger = logging.getLogger(__name__)
OPAC_WEBAPP_DB_NAME = get_opac_webapp_db_name()


class IssueLoader(BaseLoader):
    transform_model_class = TransformIssue
    transform_model_name = 'TransformIssue'
    transform_model_instance = None

    opac_model_class = OpacIssue
    opac_model_name = 'OpacIssue'
    opac_model_instance = None

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
        'bibliographic_legend',
        'pid'
    ]

    def prepare_journal(self):
        t_journal_uuid = self.transform_model_instance.journal
        t_journal_uuid_str = str(t_journal_uuid).replace("-", "")
        with switch_db(OpacJournal, OPAC_WEBAPP_DB_NAME):
            opac_journal = OpacJournal.objects.get(
                _id=t_journal_uuid_str)
        return opac_journal

    def prepare_bibliographic_legend(self):
        return "USAR LEGENDARIUM"
