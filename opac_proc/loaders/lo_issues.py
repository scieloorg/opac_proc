# coding: utf-8
from mongoengine.context_managers import switch_db
from mongoengine import DoesNotExist

from opac_proc.datastore.mongodb_connector import get_opac_webapp_db_name
from opac_proc.loaders.base import BaseLoader
from opac_proc.datastore.models import (
    TransformCollection,
    TransformJournal,
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
        'pid'
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
                logger.error(u"Journal (_id: %s) não encontrado. Já fez o Load Journal?" % transformed_coll_uuid_str)
                raise e
        return opac_journal
