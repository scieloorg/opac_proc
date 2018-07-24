# coding: utf-8
import json
import os
import sys
import logging
import logging.config

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)
from opac_proc.source_sync.utils import (
    chunks,
    MODEL_NAME_LIST,
    STAGE_LIST,
    ACTION_LIST,
    parse_date_str_to_datetime_obj,
    parse_journal_issn_from_issue_code,
    parse_journal_issn_from_article_code,
    parse_issue_pid_from_article_code,
    parse_date_str_to_datetime_obj,
)
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.source_sync.event_logger import create_sync_event_record
from opac_proc.source_sync.ids_data_retriever import (
    CollectionIdDataRetriever,
    JournalIdDataRetriever,
    IssueIdDataRetriever,
    ArticleIdDataRetriever,
    NewsIdDataRetriever,
    PressReleaseDataRetriever,
)

from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.datastore.identifiers_models import ArticleIdModel

logger = logging.getLogger(__name__)
logger_ini = os.path.join(os.path.dirname(__file__), 'logging.ini')
logging.config.fileConfig(logger_ini, disable_existing_loggers=False)


RETRIEVERS_BY_MODEL = {
    'collection': CollectionIdDataRetriever,
    'journal': JournalIdDataRetriever,
    'issue': IssueIdDataRetriever,
    'article': ArticleIdDataRetriever,
    'news': NewsIdDataRetriever,
    'press_release': PressReleaseDataRetriever,
}


def task_retrive_articles_ids_by_chunks(article_ids_chunk):
    retirever_class = RETRIEVERS_BY_MODEL['article']
    retriever_instance = retirever_class()
    for article_id in article_ids_chunk:
        retriever_instance.run_for_one_id(article_id)


def task_retrive_all_articles_ids():
    retirever_class = RETRIEVERS_BY_MODEL['article']
    retriever_instance = retirever_class()
    r_queues = RQueues()

    identifiers = retriever_instance.get_data_source_identifiers()
    list_of_all_ids = [identifier for identifier in identifiers]
    list_of_list_of_ids = list(chunks(list_of_all_ids, 1000))

    for list_of_ids in list_of_list_of_ids:
        r_queues.enqueue(
            'sync_ids', 'article',
            task_retrive_articles_ids_by_chunks, list_of_ids)


def task_call_data_retriver_by_model(model, force_serial=False):
    if model == 'article' and not force_serial:
        task_retrive_all_articles_ids()
    else:
        retirever_class = RETRIEVERS_BY_MODEL[model]
        retriever_instance = retirever_class()
        retriever_instance.run_serial_for_all()


def enqueue_ids_data_retriever(model_name='all'):
    if model_name == 'all':
        models_list = MODEL_NAME_LIST
    else:
        models_list = [model_name]

    r_queues = RQueues()
    for model_ in models_list:
        task_fn = task_call_data_retriver_by_model
        logger.info('Enfilerando task: %s para o model: %s.' % (task_fn, model_))
        create_sync_event_record(
            'sync_ids', model_, 'enqueue_ids_data_retriever',
            u'Inciando enfileramento para recuperar dados do IdModel model: %s' % model_name)
        r_queues.enqueue('sync_ids', model_, task_fn, model_)
        logger.info('Fim: Enfilerando task: %s para o model: %s.' % (task_fn, model_))
        create_sync_event_record(
            'sync_ids', model_, 'enqueue_ids_data_retriever',
            u'Fim do enfileramento para recuperar dados do IdModel model: %s' % model_name)


def serial_run_ids_data_retriever(model_name='all'):

    if model_name == 'all':
        models_list = MODEL_NAME_LIST
    else:
        models_list = [model_name]

    for model_ in models_list:
        logger.info(u'Iniciando execução SERIAL para obter dados do IdModel, para o model: %s.' % (model_))
        task_call_data_retriver_by_model(model_, force_serial=True)
        logger.info(u'Fim da execução SERIAL para obter dados do IdModel, para o model: %s.' % (model_))


def serial_retriever_article_ids(filepath):
    get_db_connection()
    with open(filepath) as fp:
        logger.info('lendo arquivo: %s', filepath)
        for line in fp:
            aid_data = json.loads(line)
            try:
                code = aid_data['code']
                new_processing_date = parse_date_str_to_datetime_obj(aid_data['processing_date'])
                art = ArticleIdModel.objects.get(article_pid=code)
            except ArticleIdModel.DoesNotExist:
                issn = parse_journal_issn_from_article_code(code)
                issue_pid = parse_issue_pid_from_article_code(code)
                new_article_data = {
                    'journal_issn': issn,
                    'issue_pid': issue_pid,
                    'article_pid': code,
                    'processing_date': aid_data['processing_date']
                }
                new_art = ArticleIdModel(**new_article_data)
                logger.info('cadastrando novo artigo: %s', aid_data)
                new_art.save()
            else:
                old_processing_date = art.processing_date
                if old_processing_date != new_processing_date:
                    # update
                    logger.info('atualizando aid: %s', code)
                    art.processing_date = new_processing_date
                    art.save()
                else:
                    logger.info(u'artigo aid: %s sem mudança de data', code)
