# coding: utf-8
import sys
import os
from datetime import datetime
import logging
import logging.config

import feedparser

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.extractors.source_clients.amapi_wrapper import custom_amapi_client
from opac_proc.extractors.source_clients.am_db.api_db_adapter import AMDBAPI
from opac_proc.datastore.models import ExtractCollection, ExtractJournal
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.datastore import identifiers_models as idmodels
from opac_proc.web import config
from opac_proc.source_sync.utils import (
    MODEL_NAME_LIST,
    parse_journal_issn_from_issue_code,
    parse_journal_issn_from_article_code,
    parse_issue_pid_from_article_code,
    parse_date_str_to_datetime_obj,
)

logger = logging.getLogger(__name__)
logger_ini = os.path.join(os.path.dirname(__file__), 'logging.ini')
logging.config.fileConfig(logger_ini, disable_existing_loggers=False)


class BaseIdDataRetriever(object):
    collection_acronym = config.OPAC_PROC_COLLECTION
    _db = None
    api_client = None
    model_name = None
    idmodel_class = None
    am_db_api = None

    def __init__(self):
        if self.model_name is None:
            raise AttributeError(u'Falta definir atributo: model_name')

        if self.idmodel_class is None:
            raise AttributeError(u'Falta definir atributo: idmodel_class')

        if self._db is None:
            self._db = get_db_connection()

        if self.api_client is None:
            self.api_client = custom_amapi_client.ArticleMeta(
                config.ARTICLE_META_THRIFT_DOMAIN,
                config.ARTICLE_META_THRIFT_PORT,
                config.ARTICLE_META_THRIFT_TIMEOUT)
        if self.am_db_api is None:
            self.am_db_api = AMDBAPI()

        super(BaseIdDataRetriever, self).__init__()

    def get_data_source_identifiers(self):
        """
        metodo que conecta com a fonte (API) e retorna um iterável com os dados
        """
        raise NotImplementedError(u'deve ser implementada na subclase')

    def _get_or_create_model_instance(self, model_selector_filter_dict):
        """
        consulta o banco usando os filtros definidos em: `model_selector_filter_dict`
        - caso existe um registro: retorna ele
        - caso não existe: cria um novo registro com os valores definidos em: `model_selector_filter_dict`
        """

        obj = self.idmodel_class.objects.filter(**model_selector_filter_dict)

        if obj.count() == 0:
            new_obj = self.idmodel_class(**model_selector_filter_dict)
            new_obj.save()
            return new_obj
        elif obj.count() == 1:
            return obj.first()
        else:
            error_msg = u'Muitos documentos retornados (modelo: %s) com a query: %s' % (
                self.model_name, model_selector_filter_dict)
            raise Exception(error_msg)

    def _update_model_instance(self, obj_filter_dict, new_data_dict):
        """
        atualizo o registro no banco, buscando pelo "obj_filter_dict"
        e mudando os campos "new_data_dict"
        """
        obj = self._get_or_create_model_instance(obj_filter_dict)
        obj.modify(**new_data_dict)

    def data_has_changed(self, raw_data):
        """
        metodo que retorna booleano aonde indica se a data mudou ou não,
        comparando raw_data com o armazenado no banco
        """
        raise NotImplementedError(u'deve ser implementada na subclase')

    def process_one_identifier(self, identifier_data):
        """
        Método que tem que ser implementado em cada subclasse
        para processar um identifier só.
        """
        raise NotImplementedError(u'deve ser implementada na subclase')

    def run_for_one_id(self, identifier):
        """
        Processamento genêrico de um "identifier" (item retornado pela API)
        Geralmente é para fazer:
            1. obtemos os dados do identifiier: self.get_identifier_data(identifier)
            2. chamamos o método: self.process_one_identifier(data) aonde data é a saida do anterior
        """
        data = self.get_identifier_data(identifier)
        self.process_one_identifier(data)

    def run_serial_for_all(self):
        """
        Método padrão:
            1. coletamos a lista completa de identifiers via API
            2. iteramos em cada item
            3. para cada item:
                3.1 coletamos os dados de cada item: self.get_identifier_data(...)
                3.2 atualizamos os dados
        """
        identifiers = self.get_data_source_identifiers()
        for identifier_doc in identifiers:
            self.run_for_one_id(identifier_doc)


# --------------------------------------------------- #
#                   COLLECTION                        #
# --------------------------------------------------- #


class CollectionIdDataRetriever(BaseIdDataRetriever):
    """ Recupera os identifiers da Collection do AM """
    model_name = 'collection'
    idmodel_class = idmodels.CollectionIdModel

    def get_data_source_identifiers(self):
        """
        Obtemos os dados do modelo fornecidos pela API da fonte
        """
        collection_ids = self.am_db_api.get_collections_identifiers()
        for col in collection_ids:
            if col['code'] == self.collection_acronym:
                _raw_data = col
                break
        if _raw_data:
            return [col, ]
        else:
            raise Exception(u'Coleção com acronym: %s não foi encontrada' % self.collection_acronym)

    def get_extract_model_instance(self):
        """
        Retorna a instancia do modelo: ExtractCollection procurando pelo acronimo
        Caso a coleção não exista, retorna None
        """
        ex_collections = ExtractCollection.objects.filter(code=self.collection_acronym)
        ex_collections_count = ex_collections.count()
        if ex_collections_count == 0:
            return None
        elif ex_collections_count == 1:
            return ex_collections.first()
        else:
            raise Exception(
                u'%s registros recuperados ExtractCollection filtando pelo code: %s. Esperado só um registro.' % (
                    ex_collections_count, self.collection_acronym)
            )

    def data_has_changed(self, raw_data):
        """
        Como o identifier da coleção não tem data de modificação na resposta,
        é preciso obter a Collection da Extração, e comparar se tem alguma mudança nos campos:
        - code
        - acronym
        - acronym2letters
        - status
        - domain
        - name
        - has_analytics
        """
        ex_collection = self.get_extract_model_instance()
        if ex_collection is None:
            # A Collection nunca foi extraída. Temos que atualizar sim.
            return True
        elif hasattr(raw_data, 'processing_date'):  # api_db_adapter inject processing_date
            source_processing_date = raw_data['processing_date']
            extracted_processing_date = ex_collection['metadata']['updated_at']
            return source_processing_date > extracted_processing_date
        else:
            # A Collection foi extraída, e vamos comparar os campos salvos como os da fonte
            target_fields = [
                'code', 'status', 'domain', 'name', 'has_analytics'
            ]
            extracted_values = {field: ex_collection[field] for field in target_fields}
            source_data_values = {field: raw_data[field] for field in target_fields}
            must_update_record = False  # flag booleano de retorno, temos que atualizar ou não?

            for field_name in target_fields:
                source_value = source_data_values[field_name]  # valor do campo na fonte (AM)
                saved_value = extracted_values[field_name]  # valor salvo no banco
                if source_value != saved_value:
                    must_update_record = True
                    break
            return must_update_record

    def get_identifier_data(self, identifier):
        data = {
            'collection_acronym': identifier['code']
        }

        if hasattr(identifier, 'processing_date'):
            data['processing_date'] = identifier['processing_date']
        else:
            data['processing_date'] = datetime.now()

        return data

    def process_one_identifier(self, identifier_data):
        coll_selector = {
            'collection_acronym': self.collection_acronym
        }
        new_data = {
            'processing_date': datetime.now()
        }
        self._update_model_instance(coll_selector, new_data)

    def run_serial_for_all(self):
        _raw_data = None
        for col in self.api_client.get_collections():
            if col['code'] == self.collection_acronym:
                _raw_data = col
                break

        if _raw_data:
            if self.data_has_changed(_raw_data):
                self.process_one_identifier(_raw_data)
            else:
                logger.info(u'Não detectamos mudanças nos dados. Não precisa atualizar')
        else:
            raise Exception(u'Coleção com acronym: %s não foi encontrada' % self.collection_acronym)


# --------------------------------------------------- #
#                   JOURNALS                          #
# --------------------------------------------------- #


class JournalIdDataRetriever(BaseIdDataRetriever):
    """ Recupera os identifiers dos Journals do AM """
    model_name = 'journal'
    idmodel_class = idmodels.JournalIdModel

    def get_data_source_identifiers(self):
        """
        Obtemos os dados do modelo fornecidos pela API da fonte
        """
        journals_ids = self.am_db_api.get_journals_identifiers()
        return journals_ids

    def get_identifier_data(self, identifier):
        return {
            'issn': identifier['code'],
            'processing_date': identifier['processing_date']
        }

    def process_one_identifier(self, identifier_data):
        document_selector = {
            'collection_acronym': self.collection_acronym,
            'journal_issn': identifier_data['issn'],
        }
        # atualizo o registro no banco
        p_date = identifier_data['processing_date']
        if isinstance(p_date, datetime):
            new_data = {
                'processing_date': p_date
            }
        else:
            new_data = {
                'processing_date': parse_date_str_to_datetime_obj(p_date)
            }
        self._update_model_instance(document_selector, new_data)


# --------------------------------------------------- #
#                   ISSUES                            #
# --------------------------------------------------- #


class IssueIdDataRetriever(BaseIdDataRetriever):
    """ Recupera os identifiers dos Issues do AM """
    model_name = 'issue'
    idmodel_class = idmodels.IssueIdModel

    def get_data_source_identifiers(self):
        """
        Obtemos os dados do modelo fornecidos pela API da fonte
        """
        issues_ids = self.am_db_api.get_issues_identifiers()
        return issues_ids

    def get_identifier_data(self, identifier):
        code = identifier['code']
        issn = parse_journal_issn_from_issue_code(code)
        proc_date = identifier['processing_date']

        return {
            'issn': issn,  # primeiros 8 ou 9 chars do "code"
            'issue_pid': code,
            'processing_date': proc_date
        }

    def process_one_identifier(self, identifier_data):
        document_selector = {
            'collection_acronym': self.collection_acronym,
            'journal_issn': identifier_data['issn'],
            'issue_pid': identifier_data['issue_pid'],
        }
        # atualizo o registro no banco
        p_date = identifier_data['processing_date']
        if isinstance(p_date, datetime):
            new_data = {
                'processing_date': p_date
            }
        else:
            new_data = {
                'processing_date': parse_date_str_to_datetime_obj(p_date)
            }
        self._update_model_instance(document_selector, new_data)


# --------------------------------------------------- #
#                   ARTICLE                           #
# --------------------------------------------------- #


class ArticleIdDataRetriever(BaseIdDataRetriever):
    """ Recupera os identifiers dos Articles do AM """
    model_name = 'article'
    idmodel_class = idmodels.ArticleIdModel

    def get_data_source_identifiers(self):
        """
        Obtemos os dados do modelo fornecidos pela API da fonte
        """
        articles_ids = self.am_db_api.get_articles_identifiers()
        return articles_ids

    def get_identifier_data(self, identifier):
        code = identifier['code']
        proc_date = identifier['processing_date']
        issn = parse_journal_issn_from_article_code(code)
        issue_pid = parse_issue_pid_from_article_code(code)

        return {
            'issn': issn,  # primeiros 8 ou 9 chars do "code"
            'issue_pid': issue_pid,  # primeiros 15 ou 16 chars do "code"
            'article_pid': code,
            'processing_date': proc_date
        }

    def process_one_identifier(self, identifier_data):
        document_selector = {
            'collection_acronym': self.collection_acronym,
            'journal_issn': identifier_data['issn'],
            'issue_pid': identifier_data['issue_pid'],
            'article_pid': identifier_data['article_pid'],
        }
        p_date = identifier_data['processing_date']
        if isinstance(p_date, datetime):
            new_data = {
                'processing_date': p_date
            }
        else:
            new_data = {
                'processing_date': parse_date_str_to_datetime_obj(p_date)
            }
        self._update_model_instance(document_selector, new_data)


# --------------------------------------------------- #
#                    NEWS                             #
# --------------------------------------------------- #


class NewsIdDataRetriever(BaseIdDataRetriever):
    """ Recupera os identifiers dos News do AM """
    model_name = 'news'
    idmodel_class = idmodels.NewsIdModel

    def get_feed_entries(self, feed_url):
        feed = feedparser.parse(feed_url)
        if feed.bozo == 1:
            bozo_exception_msg = feed.bozo_exception.getMessage()
            msg = 'Não é possível parsear o feed (%s). Bozo exception message: %s' % (
                self.url, bozo_exception_msg)
            raise Exception(msg)
        else:
            return feed['entries']

    def get_identifier_data(self, raw_entry):
        return {
            'url_id': raw_entry['id'],
            'published': parse_date_str_to_datetime_obj(raw_entry['published'])
        }

    def get_data_source_identifiers(self):
        """
        Obtemos os dados do modelo fornecidos pela feed de noticias, nos 3 idiomas
        """
        _identifiers = []
        for lang, feed in config.RSS_NEWS_FEEDS.items():
            logger.debug(u"consultando press release (lang: %s), feed: %s" % (lang, feed))
            feed_url_by_lang = feed['url'].format(lang)  # ex: http://blog.scielo.org/en/feed/
            feed_entries_list = self.get_feed_entries(feed_url_by_lang)
            for raw_feed_entry in feed_entries_list:
                _identifiers.append(raw_feed_entry)
        return _identifiers

    def process_one_identifier(self, identifier_data):
        document_selector = {
            'collection_acronym': self.collection_acronym,
            'url_id': identifier_data['url_id'],
        }
        new_date = {
            'processing_date': identifier_data['published']
        }
        self._update_model_instance(document_selector, new_date)


# --------------------------------------------------- #
#               PRESS RELEASES                        #
# --------------------------------------------------- #


class PressReleaseDataRetriever(BaseIdDataRetriever):
    """ Recupera os identifiers dos Press Release do AM """
    model_name = 'press_release'
    idmodel_class = idmodels.PressReleaseIdModel

    def get_journals_acronym(self):
        """
        É preciso uma lista de acrónimos de cada periódico extraído.
        No output capturado de /journals/identifiers não forence o acronym, só o ISSN
        """
        acronyms = []
        for journal in self.api_client.get_xylose_journals(collection=self.collection_acronym):
            acronyms.append(journal.acronym)
        return acronyms

    def get_feed_entries(self, feed_url):
        feed = feedparser.parse(feed_url)
        if feed.bozo == 1:
            bozo_exception_msg = feed.bozo_exception.getMessage()
            msg = u'Não é possível parsear o feed (%s). Bozo exception message: %s' % (
                self.url, bozo_exception_msg)
            raise Exception(msg)
        else:
            return feed['entries']

    def get_identifier_data(self, raw_entry):
        return {
            'url_id': raw_entry['id'],
            'published': parse_date_str_to_datetime_obj(raw_entry['published'])
        }

    def get_data_source_identifiers(self):
        """
        Obtemos os dados do modelo fornecidos pela feed de press release, nos 3 idiomas.
        Temos que iterar sobre todos os acronimos de cada periódico.
        """
        _identifiers = []
        for journal_acronym in self.get_journals_acronym():
            for lang, feed in config.RSS_PRESS_RELEASES_FEEDS_BY_CATEGORY.items():
                feed_url_by_lang = feed['url'].format(lang, journal_acronym)
                feed_entries_list = self.get_feed_entries(feed_url_by_lang)
                for raw_feed_entry in feed_entries_list:
                    _identifiers.append(raw_feed_entry)
        return _identifiers

    def process_one_identifier(self, identifier_data):
        document_selector = {
            'collection_acronym': self.collection_acronym,
            'url_id': identifier_data['url_id'],
        }
        new_date = {
            'processing_date': identifier_data['published']
        }
        self._update_model_instance(document_selector, new_date)
