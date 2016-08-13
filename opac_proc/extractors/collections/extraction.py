# coding: utf-8
from __future__ import unicode_literals
from opac_proc.extractors.source_clients.thrift import am_clients
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.datastore.models.collection import Collection
import logging
import config


logger = logging.getLogger(__name__)


class CExtactor(object):
    """docstring for CExtactor"""
    acronym = None
    db = None
    raw_data = []
    articlemeta = None

    extract_attributes = [
        # atributos a serem extraidos
        'code',
        'name',
        'acronym',
    ]

    def __init__(self, acronym):
        self.acronym = acronym
        self.db = get_db_connection()
        self.articlemeta = am_clients.ArticleMeta(
            config.ARTICLE_META_THRIFT_DOMAIN,
            config.ARTICLE_META_THRIFT_PORT)

    def extract(self):
        """
        Conecta com a fonte (AM) e extrai todos os dados (coleção).
        -> método: get_raw_data para obter os resultados do extract
        -> método: save() para salvar
        -> método: to_python() para retornar os dados coletados como objetos pytho (dict/lists)
        """
        for col in self.articlemeta.collections():
            if col.acronym == self.acronym:
                logger.info(u"Adicionado a coleção: %s" % self.acronym)
                self.raw_data.append(col)
                break

    def filter_raw_data(self):
        return 'TODO!'

    @property
    def get_raw_data(self):
        """
        Retorna a todos os dados coletados de forma crúa (objetos thrift)
        """
        return self.raw_data

    def save(self):
        """"
        Salva os dados coletados no datastore (mongo)
        """

        try:
            if self.raw_data:
                c = Collection()
                c.acronym = raw_data.acronym
                c.name = raw_data.name
            else:
                logger.error("Não foi possível salvar a Coleção (acronym: %s). A informação é vazía" % self.acronym)
        except Exception, e:
            logger.error("Não foi possível salvar a Coleção (acronym: %s). %s" % (self.acronym, str(e)))
            raise e

