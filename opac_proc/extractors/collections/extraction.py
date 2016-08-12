# coding: utf-8
from __future__ import unicode_literals
from opac_proc.extractors.source_clients.thrift import am_clients
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.datastore.models.collection import Collection
import logging


logger = logging.getLogger(__name__)


class CExtactor(object):
    """docstring for CExtactor"""
    acronym = None
    db = None
    raw_data = None

    def __init__(self, acronym):
        self.acronym = acronym
        self.db = get_db_connection()

    def run(self):
        # Collection
        for col in articlemeta.collections():
            if col.acronym == self.acronym:
                logger.info(u"Adicionado a coleção: %s" % self.acronym)
                self.raw_data = col
                break

    def save(self):
        """" docstring aqui """
        try:
            if self.raw_data:
                c = Collection()
                c.acronym = raw_data.acronym
                c.name = raw_data.name
            else:
                logger.error("Não foi possível salvar a Coleção (acronym: %s). A informação é vazía" % self.acronym)
        except Exception, e:
            logger.error("Não foi possível salvar a Coleção (acronym: %s). %s" % (self.acronym, str(e)))
