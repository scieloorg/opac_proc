# coding: utf-8
from mongoengine.context_managers import switch_db
from mongoengine import DoesNotExist

from opac_proc.datastore.mongodb_connector import get_opac_webapp_db_name
from opac_proc.loaders.base import BaseLoader
from opac_proc.datastore.models import (
    LoadPressRelease,
    TransformPressRelease)

from opac_schema.v1.models import Journal as OpacJournal
from opac_schema.v1.models import PressRelease as OpacPressRelease


from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "load")
else:
    logger = getMongoLogger(__name__, "INFO", "load")

OPAC_WEBAPP_DB_NAME = get_opac_webapp_db_name()


class PressReleaseLoader(BaseLoader):
    transform_model_class = TransformPressRelease
    transform_model_instance = None

    opac_model_class = OpacPressRelease
    opac_model_instance = None

    load_model_class = LoadPressRelease
    load_model_instance = None

    fields_to_load = [
        'journal',
        'title',
        'language',
        'content',
        'url',
        'publication_date',
        'created',
        'updated',
    ]

    def prepare_journal(self):
        """
        metodo chamado na preparação dos dados a carregar no opac_schema
        deve retornar um valor válido para PressRelease.journal
        """
        logger.debug(u"iniciando: prepare_journal")
        t_journal_acronym = self.transform_model_instance.journal_acronym

        try:
            with switch_db(OpacJournal, OPAC_WEBAPP_DB_NAME) as OPAC_Journal:
                opac_journal = OPAC_Journal.objects.get(acronym=t_journal_acronym)
                return opac_journal
        except DoesNotExist, e:
            logger.error(
                u"Journal (acronym: %s) não foi encontrado. Já fez o Load Journal?",
                t_journal_acronym)
            raise e
