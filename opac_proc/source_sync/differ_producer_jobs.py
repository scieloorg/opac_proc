# coding: utf-8
import sys
import os
import logging
import logging.config
from datetime import datetime, timedelta

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)


from opac_proc.web.config import DEFAULT_DIFF_SPAN  # importado assim para contornar o app_context
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.source_sync.utils import MODEL_NAME_LIST, ACTION_LIST, STAGE_LIST
from opac_proc.source_sync.event_logger import create_sync_event_record
from opac_proc.source_sync.differ import (
    CollectionDiffer,
    JournalDiffer,
    IssueDiffer,
    ArticleDiffer,
    PressReleaseDiffer,
    NewsDiffer,
)

logger = logging.getLogger(__name__)
logger_ini = os.path.join(os.path.dirname(__file__), 'logging.ini')
logging.config.fileConfig(logger_ini, disable_existing_loggers=False)

DIFFERS = {
    'collection': CollectionDiffer,
    'journal': JournalDiffer,
    'issue': IssueDiffer,
    'article': ArticleDiffer,
    'news': PressReleaseDiffer,
    'press_release': NewsDiffer,
}


# -------------------------------------------------- #
#                    ADD                             #
# -------------------------------------------------- #


def task_differ_add(stage, model_name):
    logger.info("differ_producer_jobs::task_differ_add(stage: %s, model_name: %s)" % (stage, model_name))
    diff_class = None

    if model_name not in MODEL_NAME_LIST:
        raise ValueError('Param: model_name:%s com valor inesperado!' % model_name)
    else:
        logger.info("[%s][%s] Coletando: ADD para o modelo" % (stage, model_name))
        diff_class = DIFFERS[model_name]
        diff_class_instance = diff_class()
        uuids_to_add = diff_class_instance.collect_add_records(stage)
        logger.info("[%s][%s] Coletados: %s documentos para ADD: " % (stage, model_name, len(uuids_to_add)))
        for uuid in uuids_to_add:
            diff_class_instance.create_diff_model(stage, 'add', uuid)


# ------------------------------------------------------ #
#                     UPDATE                             #
# ------------------------------------------------------ #


def task_differ_update(stage, model_name, since_date=None):
    if since_date is None:
        since_date = datetime.today() - timedelta(days=DEFAULT_DIFF_SPAN)

    logger.info("differ_producer_jobs::task_differ_update(stage: %s, model_name: %s, since_date=%s)" % (stage, model_name, since_date))
    diff_class = None

    if model_name not in MODEL_NAME_LIST:
        raise ValueError('Param: model_name:%s com valor inesperado!' % model_name)
    else:
        logger.info("[%s][%s] Coletando: ADD para o modelo" % (stage, model_name))
        diff_class = DIFFERS[model_name]
        diff_class_instance = diff_class()
        uuids_to_update = diff_class_instance.collect_update_records(stage, since_date)
        logger.info("[%s][%s] Coletados: %s documentos para UPDATE: " % (stage, model_name, len(uuids_to_update)))
        for uuid in uuids_to_update:
            diff_class_instance.create_diff_model(stage, 'update', uuid)


# ------------------------------------------------------ #
#                     DELETE                             #
# ------------------------------------------------------ #


def task_differ_delete(stage, model_name):
    logger.info("differ_producer_jobs::task_differ_delete(stage: %s, model_name: %s)" % (stage, model_name))
    diff_class = None

    if model_name not in MODEL_NAME_LIST:
        raise ValueError('Param: model_name:%s com valor inesperado!' % model_name)
    else:
        logger.info("[%s][%s] Coletando: DELETE para o modelo: " % (stage, model_name))
        diff_class = DIFFERS[model_name]
        diff_class_instance = diff_class()
        uuids_to_delete = diff_class_instance.collect_delete_records(stage)
        logger.info("[%s][%s] Coletados: %s documentos para DELETE" % (stage, model_name, len(uuids_to_delete)))
        for uuid in uuids_to_delete:
            diff_class_instance.create_diff_model(stage, 'delete', uuid)


# ---------------------------------------------------- #
#                    GERAL                             #
# ---------------------------------------------------- #


def enqueue_differ_producer_tasks(stage='all', model_name='all', action='all'):
    create_sync_event_record(
        'sync_ids', 'all', 'enqueue_differ_producer_tasks',
        u'Inciando enfileramento para producir registros diff: stage %s model: %s: action: %s' % (
            stage, model_name, action))
    if stage == 'all':
        stages_list = STAGE_LIST
    elif stage not in STAGE_LIST:
        raise ValueError('Param: stage: %s com valor inesperado!' % stage)
    else:
        stages_list = [stage, ]

    if model_name == 'all':
        models_list = MODEL_NAME_LIST
    else:
        models_list = [model_name]

    if action == 'all':
        actions_list = ACTION_LIST
    else:
        actions_list = [action, ]

    r_queues = RQueues()
    task_fn_by_action = {
        'add': task_differ_add,
        'update': task_differ_update,
        'delete': task_differ_delete
    }

    for stage_ in stages_list:
        for model_ in models_list:
            for action_ in actions_list:
                task_fn = task_fn_by_action[action_]
                r_queues.enqueue('sync_ids', model_, task_fn, stage_, model_)
                create_sync_event_record(
                    'sync_ids', model_, 'task_differ_%s' % action_,
                    u'Fim do enfileramento para producir registros diff: stage %s model: %s: action: %s' % (
                        stage_, model_, action_)
                )

    create_sync_event_record(
        'sync_ids', 'all', 'enqueue_differ_producer_tasks',
        u'Fim do enfileramento para producir registros diff: stage %s model: %s: action: %s' % (
            stage, model_name, action))
