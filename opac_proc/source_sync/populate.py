# coding: utf-8
import sys
import os
import logging
import logging.config

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.datastore.models import (
    ExtractCollection,
    ExtractJournal,
    ExtractIssue,
    ExtractArticle,
    ExtractNews,
    ExtractPressRelease,
    TransformCollection,
    TransformJournal,
    TransformIssue,
    TransformArticle,
    TransformNews,
    TransformPressRelease,
    LoadCollection,
    LoadJournal,
    LoadIssue,
    LoadArticle,
    LoadNews,
    LoadPressRelease,
)

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


class PopulateBase(object):
    collection_acronym = config.OPAC_PROC_COLLECTION
    _db = None
    model_name = None
    id_model_class = None
    ex_model_class = None
    tr_model_class = None
    lo_model_class = None

    def __init__(self):
        if self.model_name is None:
            raise AttributeError(u'Falta definir atributo: model_name')

        if self.id_model_class is None:
            raise AttributeError(u'Falta definir atributo: id_model_class')

        if self.ex_model_class is None:
            raise AttributeError(u'Falta definir atributo: ex_model_class')

        if self.tr_model_class is None:
            raise AttributeError(u'Falta definir atributo: tr_model_class')

        if self._db is None:
            self._db = get_db_connection()

    def get_id_model_lookup_filters(self, filter_values):
        """
        retorna um dicioario de campos/valores que deve ser usada para recuperar o modelo identifier
        Ex:
        - collection:   {'collection_acronym': 'spa' }
        - journals:     {'collection_acronym': 'spa', 'journal_issn': '123' }
        - issue:        {'collection_acronym': 'spa', 'journal_issn': '123', 'issue_pid': '456' }
        - articles:     {'collection_acronym': 'spa', 'journal_issn': '123', 'issue_pid': '456', 'article_pid': '789' }
        - news:         {'collection_acronym': 'spa', 'url_id': 'http://123/?p=1'}
        - press_release:{'collection_acronym': 'spa', 'url_id': 'http://345/?p=2'}
        """
        raise NotImplementedError(u'deve ser implementada na subclase')

    def prepare_data_to_identifier_data(self, extract_model_instance):
        """
        metodo que retorna um dicionario pronto para salvar como modelo de identificador (idsmodels instance)
        """
        raise NotImplementedError(u'deve ser implementada na subclase')

    def _get_model_instance_by_uuid(self, model_class, uuid):
        """
        retorna a instância do modelo tranform, buscando pelo UUID do extract.
        """

        obj = model_class.objects.filter(uuid=uuid)
        obj_count = obj.count()

        if obj_count == 0:
            return None  # o docuemnto não foi salvo ainda
        elif obj_count == 1:
            return obj.first()
        else:
            raise ValueError(u'%s objetos retornado. Esperava 1 docuemnto só.Modelo: %s UUID: %s' % (
                obj_count, self.model_name, uuid))

    def _get_tranform_execution_date_by_uuid(self, uuid):
        tr_model_instance = self._get_model_instance_by_uuid(
            model_class=self.tr_model_class, uuid=uuid)
        # se houver modelo transformado (T): recuperamos o campo: T.metadata.process_finish_at
        if tr_model_instance:
            transform_execution_date = tr_model_instance['metadata']['process_finish_at']
        else:
            logger.info("transform model instance not found: model name: %s uuid: %s" % (self.model_name, uuid))
            transform_execution_date = None
        return transform_execution_date

    def _get_load_execution_date_by_uuid(self, uuid):
        lo_model_instance = self._get_model_instance_by_uuid(
            model_class=self.lo_model_class, uuid=uuid)
        # se houver modelo carregado (L): recuperamos o campo: L.metadata.process_finish_at
        if lo_model_instance:
            load_execution_date = lo_model_instance['metadata']['process_finish_at']
        else:
            logger.info("load model instance not found: model name: %s uuid: %s" % (self.model_name, uuid))
            load_execution_date = None
        return load_execution_date

    def _get_or_create_id_model_instance(self, id_model_selector_filter_dict):
        """
        consulta o banco usando os filtros definidos em: `id_model_selector_filter_dict`
        - caso existe um registro: retorna ele
        - caso não existe: cria um novo registro com os valores definidos em: `id_model_selector_filter_dict`
        """
        obj = self.id_model_class.objects.filter(**id_model_selector_filter_dict)

        if obj.count() == 0:
            new_obj = self.id_model_class(**id_model_selector_filter_dict)
            new_obj.save()
            return new_obj
        elif obj.count() == 1:
            return obj.first()
        else:
            error_msg = u'Muitos documentos retornados (modelo: %s) com a query: %s' % (
                self.model_name, id_model_selector_filter_dict)
            raise Exception(error_msg)

    def save_identifier_model(self, obj_filter_dict, new_data_dict):
        """
        metodo que conecta com o banco e retorna uma instância do modelo extraido
        """
        obj = self._get_or_create_id_model_instance(obj_filter_dict)
        obj.modify(**new_data_dict)

    def run_for_one_model_instance(self, ex_model_instance):
        """
        Executa o processo de populate para um modelo de extração.
        Recebe uma instância do modelo: "ex_model_instance"
        """
        ex_data_dict = self.prepare_data_to_identifier_data(ex_model_instance)
        id_models_filter = self.get_id_model_lookup_filters(ex_data_dict)
        self.save_identifier_model(id_models_filter, ex_data_dict)

    def run_for_one_model_instance_by_uuid(self, ex_model_instance_uuid):
        """
        Executa o processo de populate para um modelo de extração.
        Recebe um UUID ("ex_model_instance_uuid") do modelo para pegar uma instância do modelo e processar.
        Caso não encontrar o modelo, vai levantar uma exeção
        """
        try:
            ex_model_instance = self.ex_model_class.objects.get(uuid=ex_model_instance_uuid)
        except self.ex_model_class.DoesNotExist as e:
            raise e
        else:
            self.run_for_one_model_instance(ex_model_instance)

    def run_serial_for_all(self):
        """
        execução genêrica:
        - percorremos cada objeto salvo na extração, do modelo: self.ex_model_class
            1. obtemos um dict com os dados do modelo extraído, só os campos necessários de tudo que foi extraído
            2. usamos o dict (passo 1) para criar um filtro e recuparar o idmodel no banco
            3. atualizamos os dados do id_model com o dict (passo 1)
        """
        for ex_model_instance in self.ex_model_class.objects:
            self.run_for_one_model_instance(ex_model_instance)


class PopulateCollection(PopulateBase):

    model_name = 'collection'
    id_model_class = idmodels.CollectionIdModel
    ex_model_class = ExtractCollection
    tr_model_class = TransformCollection
    lo_model_class = LoadCollection

    def get_id_model_lookup_filters(self, filter_values):
        return {
            'collection_acronym': self.collection_acronym
        }

    def prepare_data_to_identifier_data(self, extract_model_instance):
        processing_date = extract_model_instance['metadata']['process_finish_at']
        extract_execution_date = extract_model_instance['metadata']['process_finish_at']
        # procuparmos preencher os campos de data de execução: Tranform e Load
        uuid = extract_model_instance['uuid']
        transform_execution_date = self._get_tranform_execution_date_by_uuid(uuid)
        load_execution_date = self._get_load_execution_date_by_uuid(uuid)

        return {
            'uuid': extract_model_instance['uuid'],
            'collection_acronym': self.collection_acronym,
            'processing_date': processing_date,
            'extract_execution_date': extract_execution_date,
            'transform_execution_date': transform_execution_date,
            'load_execution_date': load_execution_date,
        }


class PopulateJournal(PopulateBase):

    model_name = 'journal'
    id_model_class = idmodels.JournalIdModel
    ex_model_class = ExtractJournal
    tr_model_class = TransformJournal
    lo_model_class = LoadJournal

    def get_id_model_lookup_filters(self, filter_values):
        return {
            'collection_acronym': self.collection_acronym,
            'journal_issn': filter_values['journal_issn'],
        }

    def prepare_data_to_identifier_data(self, extract_model_instance):
        extracted_code = extract_model_instance['code']
        processing_date = parse_date_str_to_datetime_obj(extract_model_instance['processing_date'])
        extract_execution_date = extract_model_instance['metadata']['process_finish_at']
        # procuparmos preencher os campos de data de execução: Tranform e Load
        uuid = extract_model_instance['uuid']
        transform_execution_date = self._get_tranform_execution_date_by_uuid(uuid)
        load_execution_date = self._get_load_execution_date_by_uuid(uuid)
        return {
            'uuid': extract_model_instance['uuid'],
            'collection_acronym': self.collection_acronym,
            'journal_issn': extracted_code,
            'processing_date': processing_date,
            'extract_execution_date': extract_execution_date,
            'transform_execution_date': transform_execution_date,
            'load_execution_date': load_execution_date,
        }


class PopulateIssue(PopulateBase):

    model_name = 'issue'
    id_model_class = idmodels.IssueIdModel
    ex_model_class = ExtractIssue
    tr_model_class = TransformIssue
    lo_model_class = LoadIssue

    def get_id_model_lookup_filters(self, filter_values):
        return {
            'collection_acronym': self.collection_acronym,
            'journal_issn': filter_values['journal_issn'],
            'issue_pid': filter_values['issue_pid'],
        }

    def prepare_data_to_identifier_data(self, extract_model_instance):
        extracted_code = extract_model_instance['code']
        journal_issn = parse_journal_issn_from_issue_code(extracted_code)
        issue_pid = extracted_code
        processing_date = parse_date_str_to_datetime_obj(extract_model_instance['processing_date'])
        extract_execution_date = extract_model_instance['metadata']['process_finish_at']
        # procuparmos preencher os campos de data de execução: Tranform e Load
        uuid = extract_model_instance['uuid']
        transform_execution_date = self._get_tranform_execution_date_by_uuid(uuid)
        load_execution_date = self._get_load_execution_date_by_uuid(uuid)
        return {
            'uuid': extract_model_instance['uuid'],
            'collection_acronym': self.collection_acronym,
            'journal_issn': journal_issn,
            'issue_pid': issue_pid,
            'processing_date': processing_date,
            'extract_execution_date': extract_execution_date,
            'transform_execution_date': transform_execution_date,
            'load_execution_date': load_execution_date,
        }


class PopulateArticle(PopulateBase):

    model_name = 'article'
    id_model_class = idmodels.ArticleIdModel
    ex_model_class = ExtractArticle
    tr_model_class = TransformArticle
    lo_model_class = LoadArticle

    def get_id_model_lookup_filters(self, filter_values):
        return {
            'collection_acronym': self.collection_acronym,
            'journal_issn': filter_values['journal_issn'],
            'issue_pid': filter_values['issue_pid'],
            'article_pid': filter_values['article_pid'],
        }

    def prepare_data_to_identifier_data(self, extract_model_instance):
        extracted_code = extract_model_instance['code']
        journal_issn = parse_journal_issn_from_article_code(extracted_code)
        issue_pid = parse_issue_pid_from_article_code(extracted_code)
        article_pid = extracted_code
        processing_date = parse_date_str_to_datetime_obj(extract_model_instance['processing_date'])
        extract_execution_date = extract_model_instance['metadata']['process_finish_at']
        # procuparmos preencher os campos de data de execução: Tranform e Load
        uuid = extract_model_instance['uuid']
        transform_execution_date = self._get_tranform_execution_date_by_uuid(uuid)
        load_execution_date = self._get_load_execution_date_by_uuid(uuid)
        return {
            'uuid': extract_model_instance['uuid'],
            'collection_acronym': self.collection_acronym,
            'journal_issn': journal_issn,
            'issue_pid': issue_pid,
            'article_pid': article_pid,
            'processing_date': processing_date,
            'extract_execution_date': extract_execution_date,
            'transform_execution_date': transform_execution_date,
            'load_execution_date': load_execution_date,
        }


class PopulateNews(PopulateBase):

    model_name = 'news'
    id_model_class = idmodels.NewsIdModel
    ex_model_class = ExtractNews
    tr_model_class = TransformNews
    lo_model_class = LoadNews

    def get_id_model_lookup_filters(self, filter_values):
        return {
            'collection_acronym': self.collection_acronym,
            'url_id': filter_values['url_id'],
        }

    def prepare_data_to_identifier_data(self, extract_model_instance):
        url_id = extract_model_instance['url_id']
        processing_date = parse_date_str_to_datetime_obj(extract_model_instance['published'])
        extract_execution_date = extract_model_instance['metadata']['process_finish_at']
        # procuparmos preencher os campos de data de execução: Tranform e Load
        uuid = extract_model_instance['uuid']
        transform_execution_date = self._get_tranform_execution_date_by_uuid(uuid)
        load_execution_date = self._get_load_execution_date_by_uuid(uuid)
        return {
            'uuid': extract_model_instance['uuid'],
            'collection_acronym': self.collection_acronym,
            'url_id': url_id,
            'processing_date': processing_date,
            'extract_execution_date': extract_execution_date,
            'transform_execution_date': transform_execution_date,
            'load_execution_date': load_execution_date,
        }


class PopulatePressRelease(PopulateBase):

    model_name = 'press_release'
    id_model_class = idmodels.PressReleaseIdModel
    ex_model_class = ExtractPressRelease
    tr_model_class = TransformPressRelease
    lo_model_class = LoadPressRelease

    def get_id_model_lookup_filters(self, filter_values):
        return {
            'collection_acronym': self.collection_acronym,
            'url_id': filter_values['url_id'],
        }

    def prepare_data_to_identifier_data(self, extract_model_instance):
        url_id = extract_model_instance['url_id']
        processing_date = parse_date_str_to_datetime_obj(extract_model_instance['published'])
        extract_execution_date = extract_model_instance['metadata']['process_finish_at']
        # procuparmos preencher os campos de data de execução: Tranform e Load
        uuid = extract_model_instance['uuid']
        transform_execution_date = self._get_tranform_execution_date_by_uuid(uuid)
        load_execution_date = self._get_load_execution_date_by_uuid(uuid)
        return {
            'uuid': extract_model_instance['uuid'],
            'collection_acronym': self.collection_acronym,
            'url_id': url_id,
            'processing_date': processing_date,
            'extract_execution_date': extract_execution_date,
            'transform_execution_date': transform_execution_date,
            'load_execution_date': load_execution_date,
        }


def get_populator_class(model_name):
    if model_name == 'collection':
        populator_class = PopulateCollection()
    elif model_name == 'journal':
        populator_class = PopulateJournal()
    elif model_name == 'issue':
        populator_class = PopulateIssue()
    elif model_name == 'article':
        populator_class = PopulateArticle()
    elif model_name == 'news':
        populator_class = PopulateNews()
    elif model_name == 'press_release':
        populator_class = PopulatePressRelease()
    else:
        raise RuntimeError(u'model_name inválido')
    return populator_class


def main(model_name):
    """ script para roda manualmente """
    logger.info("main -> model_name: %s" % model_name)
    process_all = model_name == 'populate_all'
    if process_all:
        for model in MODEL_NAME_LIST:
            populator = get_populator_class(model)
            logger.info(u"executando retrieve do modelo: %s" % model)
            populator.run_serial_for_all()
            logger.info(u"finalizada retrieve do modelo: %s" % model)
    else:
        populator = get_populator_class(model_name)
        logger.info(u"executando retrieve do modelo: %s" % model_name)
        populator.run_serial_for_all()
        logger.info(u"finalizada retrieve do modelo: %s" % model_name)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "erro: falta indicar o modulo"
    main(sys.argv[1])
