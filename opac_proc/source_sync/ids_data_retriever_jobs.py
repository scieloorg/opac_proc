# coding: utf-8
import os
import sys
import logging
import logging.config

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.source_sync.utils import MODEL_NAME_LIST, STAGE_LIST, ACTION_LIST
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


def task_call_data_retriver_by_model(model):
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
        task_call_data_retriver_by_model(model_)
        logger.info(u'Fim da execução SERIAL para obter dados do IdModel, para o model: %s.' % (model_))
