# coding: utf-8
from datetime import datetime, timedelta
from pymongo import MongoClient
from opac_proc.web.config import (
    AM_MONGODB_SETTINGS,
    OPAC_PROC_COLLECTION,
    DEFAULT_DIFF_SPAN
)


class AMDBAPI:
    _client = None
    _db = None
    _projection_by_model = {
        'collection': {
            '_id': 0,
            'code': 1,
        },
        'journal': {
            '_id': 0,
            'code': 1,
            'collection': 1,
            'processing_date': 1
        },
        'issue': {
            '_id': 0,
            'code': 1,
            'collection': 1,
            'processing_date': 1
        },
        'article': {
            '_id': 0,
            'code': 1,
            'collection': 1,
            'processing_date': 1
        },
    }
    _since_date = None

    def __init__(self, days_span=None):
        """
        conecta com o banco mongo do AM e cria um instância de MongoClient

        @param: days_span (int - opcional) quantidade de dias de intervalo
                (contanto do agora para atrás no tempo). Define o intevalo de
                corte. Por padrão sera definido pela configuração:
                DEFAULT_DIFF_SPAN. A data de corte fica em: self._since_date

        """
        db_name = AM_MONGODB_SETTINGS['db']
        self._client = MongoClient(
            host=AM_MONGODB_SETTINGS['host'],
            port=AM_MONGODB_SETTINGS['port'],
            username=AM_MONGODB_SETTINGS['username'],
            password=AM_MONGODB_SETTINGS['password'],
            authSource='admin',
            authMechanism='SCRAM-SHA-1',
            readPreference='secondary',  # by default secondary is readonly
        )
        self._db = self._client[db_name]

        if days_span is None:
            days_span = DEFAULT_DIFF_SPAN
        self._since_date = datetime.now() - timedelta(days=days_span)

    @property
    def get_since_date(self):
        """
        retorna a data (datetime) de corte usado para filtar na consulta, caso
        não seja passado outra data como parametro
        """

        return self._since_date

    def get_collections_identifiers(self):
        """
        retorna os identifiers da coleção definida pela configuração.

        returna uma lista de dict()
        cada dict contém:
        - code: código da coleção;
        - processing_date: data atual (datetime.now()) pq a AM não tem data.
        """

        query_filter = {
            'code': OPAC_PROC_COLLECTION
        }
        projection = self._projection_by_model['collection']
        results_cursor = self._db.collections.find(query_filter, projection)
        docs = []
        for doc in results_cursor:
            # percorremos todos os docs inserindo o campo:
            # - processing_date = datetime.now()
            doc['processing_date'] = datetime.now()
            docs.append(doc)

        return docs

    def get_journals_identifiers(self):
        """
        retorna os identifiers de periódicos filtrando pela coleção definida
        pela configuração.

        returna uma lista de dict()
        cada dict contém:
        - code: issn do periódico;
        - collection: código da coleção;
        - processing_date: retornada pelo AM
        """

        query_filter = {
            'collection': OPAC_PROC_COLLECTION
        }
        projection = self._projection_by_model['journal']
        results = self._db.journals.find(query_filter, projection)
        docs = [doc for doc in results]
        return docs

    def get_issues_identifiers(self):
        """
        retorna os identifiers de issues filtrando pela coleção definida
        pela configuração e a data de corte.

        returna uma lista de dict()
        cada dict contém:
        - code: pid do issue;
        - collection: código da coleção;
        - processing_date: retornada pelo AM
        """

        query_filter = {
            'collection': OPAC_PROC_COLLECTION,
        }
        projection = self._projection_by_model['issue']
        results = self._db.issues.find(query_filter, projection)
        docs = [doc for doc in results]
        return docs

    def get_articles_identifiers(self, since_date=None):
        """
        retorna os identifiers de artigos filtrando pela coleção definida
        pela configuração e a data de corte.

        @param: since_date (datetime|opcional) - data de corte. se não for
        definida será usada a data retornada pela property: get_since_date

        returna uma lista de dict()
        cada dict contém:
        - code: pid do artigo;
        - collection: código da coleção;
        - processing_date: retornada pelo AM
        """

        if since_date is None:
            since_date = self._since_date

        query_filter = {
            'collection': OPAC_PROC_COLLECTION,
            'processing_date': {
                '$gte': since_date,
            }
        }
        projection = self._projection_by_model['article']
        results = self._db.articles.find(query_filter, projection)
        docs = [doc for doc in results]
        return docs
