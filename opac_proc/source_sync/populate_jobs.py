# coding: utf-8
import sys
import os
import logging
import logging.config

from mongoengine.queryset.visitor import Q

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.datastore import models
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.source_sync.utils import chunks
from opac_proc.source_sync.event_logger import create_sync_event_record
from opac_proc.source_sync.populate import (
    PopulateCollection,
    PopulateJournal,
    PopulateIssue,
    PopulateArticle,
    PopulateNews,
    PopulatePressRelease
)


logger = logging.getLogger(__name__)
logger_ini = os.path.join(os.path.dirname(__file__), 'logging.ini')
logging.config.fileConfig(logger_ini, disable_existing_loggers=False)


def generic_task_enqueue_from_uuid_iterable(stage, model_name, model_class, r_queues, target_fn, ids):

    if ids is None:  # update all collections
        if model_name == 'article':
            """
            Para os artigos filtramos registros que não tenham alguma data: extract OU transform OU load
            """
            model_instances_uuid_qs = model_class.objects.filter(
                Q(extract_execution_date=None) | Q(transform_execution_date=None) | Q(load_execution_date=None)
            ).values_list('uuid')
        else:
            model_instances_uuid_qs = model_class.objects.values_list('uuid')

        list_of_list_of_uuids = list(chunks(model_instances_uuid_qs, 1000))
        logger.debug(u"obtive: %s listas de listas de UUIDs" % len(list_of_list_of_uuids))
        for list_of_uuids in list_of_list_of_uuids:
            logger.info("enfilerando este chunk de UUIDs: %s" % list_of_uuids)
            create_sync_event_record(
                stage, model_name, target_fn,
                u'Iniciando enfileramento de todos os registros (%s) do modelo: %s' % (len(list_of_uuids), model_name))
            map(lambda uuid: r_queues.enqueue(stage, model_name, target_fn, uuid), list_of_uuids)
            create_sync_event_record(
                stage, model_name, target_fn,
                u'Finalizado enfileramento de todos os registros (%s) do modelo: %s' % (len(list_of_uuids), model_name))
    else:
        create_sync_event_record(
            stage, model_name, target_fn,
            u'Inciando enfileramento de %s registros do modelo: %s' % (len(ids), model_name))

        for oid in ids:
            try:
                obj = model_class.objects.get(pk=oid)
                uuid = obj.uuid
                r_queues.enqueue(stage, model_name, target_fn, uuid)
            except model_class.DoesNotExist as e:
                logger.error(u'Modelo (%s) não existe: %s. pk: %s' % (model_name, str(e), oid))

        create_sync_event_record(
            stage, model_name, target_fn,
            u'Finalizando enfileramento de %s registros do modelo: %s' % (len(ids), model_name))


# --------------------------------------------------- #
#                   COLLECTION                        #
# --------------------------------------------------- #


def task_populate_one_collection(uuid):
    populator_class = PopulateCollection()
    populator_class.run_for_one_model_instance_by_uuid(uuid)


def task_populate_collections(ids=None):
    get_db_connection()
    stage = 'sync_ids'
    model_name = 'collection'
    model_class = models.ExtractCollection
    r_queues = RQueues()
    target_fn = task_populate_one_collection

    generic_task_enqueue_from_uuid_iterable(stage, model_name, model_class, r_queues, target_fn, ids)


# --------------------------------------------------- #
#                   JOURNALS                          #
# --------------------------------------------------- #


def task_populate_one_journal(uuid):
    populator_class = PopulateJournal()
    populator_class.run_for_one_model_instance_by_uuid(uuid)


def task_populate_journals(ids=None):
    get_db_connection()
    stage = 'sync_ids'
    model_name = 'journal'
    model_class = models.ExtractJournal
    r_queues = RQueues()
    target_fn = task_populate_one_journal

    generic_task_enqueue_from_uuid_iterable(stage, model_name, model_class, r_queues, target_fn, ids)


# --------------------------------------------------- #
#                   ISSUES                            #
# --------------------------------------------------- #


def task_populate_one_issue(uuid):
    populator_class = PopulateIssue()
    populator_class.run_for_one_model_instance_by_uuid(uuid)


def task_populate_issues(ids=None):
    get_db_connection()
    stage = 'sync_ids'
    model_name = 'issue'
    model_class = models.ExtractIssue
    r_queues = RQueues()
    target_fn = task_populate_one_issue

    generic_task_enqueue_from_uuid_iterable(stage, model_name, model_class, r_queues, target_fn, ids)


# --------------------------------------------------- #
#                   ARTICLE                           #
# --------------------------------------------------- #


def task_populate_one_article(uuid):
    populator_class = PopulateArticle()
    populator_class.run_for_one_model_instance_by_uuid(uuid)


def task_populate_articles(ids=None):
    get_db_connection()
    stage = 'sync_ids'
    model_name = 'article'
    model_class = models.ExtractArticle
    r_queues = RQueues()
    target_fn = task_populate_one_article
    generic_task_enqueue_from_uuid_iterable(stage, model_name, model_class, r_queues, target_fn, ids)


# --------------------------------------------------- #
#               PRESS RELEASES                        #
# --------------------------------------------------- #


def task_populate_one_press_release(uuid):
    populator_class = PopulatePressRelease()
    populator_class.run_for_one_model_instance_by_uuid(uuid)


def task_populate_press_release(ids=None):
    get_db_connection()
    stage = 'sync_ids'
    model_name = 'press_release'
    model_class = models.ExtractPressRelease
    r_queues = RQueues()
    target_fn = task_populate_one_press_release
    generic_task_enqueue_from_uuid_iterable(stage, model_name, model_class, r_queues, target_fn, ids)


# --------------------------------------------------- #
#                    NEWS                             #
# --------------------------------------------------- #


def task_populate_one_news(uuid):
    populator_class = PopulateNews()
    populator_class.run_for_one_model_instance_by_uuid(uuid)


def task_populate_news(ids=None):
    get_db_connection()
    stage = 'sync_ids'
    model_name = 'news'
    model_class = models.ExtractNews
    r_queues = RQueues()
    target_fn = task_populate_one_news
    generic_task_enqueue_from_uuid_iterable(stage, model_name, model_class, r_queues, target_fn, ids)


# ---------------------------------------------------- #
#                    GERAL                             #
# ---------------------------------------------------- #


def enqueue_full_populate_task_by_model(model_name='all'):
    logger.info("Inicinado: enqueue_full_populate_task_by_model para modelo: %s", model_name)
    create_sync_event_record(
        'sync_ids', model_name, 'enqueue_full_populate_task_by_model',
        u'Inciando enfileramento para preencher datas dos registros diff model: %s' % model_name)

    # setup
    get_db_connection()
    stage = 'sync_ids'
    r_queues = RQueues()
    model_class = None
    task_fn = None

    options = {
        'collection': {
            'model_class': models.ExtractCollection,
            'task_fn': task_populate_collections
        },
        'journal': {
            'model_class': models.ExtractJournal,
            'task_fn': task_populate_journals
        },
        'issue': {
            'model_class': models.ExtractIssue,
            'task_fn': task_populate_issues
        },
        'article': {
            'model_class': models.ExtractArticle,
            'task_fn': task_populate_articles
        },
        'news': {
            'model_class': models.ExtractNews,
            'task_fn': task_populate_news
        },
        'press_release': {
            'model_class': models.ExtractPressRelease,
            'task_fn': task_populate_press_release
        }
    }

    if model_name == 'all':
        for k, v in options.items():
            model_class = v['model_class']
            task_fn = v['task_fn']
            logger.info("enfilerando stage: %s model_name: %s model_class: %s" % (stage, k, model_class))
            r_queues.enqueue(stage, k, task_fn)
    elif model_name not in options.keys():
        raise ValueError('Param: model_name: %s inesperado' % model_name)
    else:
        model_class = options[model_name]['model_class']
        task_fn = options[model_name]['task_fn']
        logger.info("enfilerando stage: %s model_name: %s model_class: %s" % (stage, model_name, model_class))
        r_queues.enqueue(stage, model_name, task_fn)

    create_sync_event_record(
        'sync_ids', model_name, 'enqueue_full_populate_task_by_model',
        u'Fim do enfileramento para preencher datas dos registros diff model: %s' % model_name)

    logger.info("Fim: enqueue_full_populate_task_by_model para modelo: %s", model_name)
