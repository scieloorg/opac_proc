# coding: utf-8
import sys
import os
import logging
import logging.config

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)


from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.source_sync.utils import MODEL_NAME_LIST, ACTION_LIST, STAGE_LIST
from opac_proc.source_sync.event_logger import create_sync_event_record
from opac_proc.source_sync.utils import chunks
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

DIFFERS = {  # mover para utils.py
    'collection': CollectionDiffer,
    'journal': JournalDiffer,
    'issue': IssueDiffer,
    'article': ArticleDiffer,
    'news': PressReleaseDiffer,
    'press_release': NewsDiffer,
}


def task_differ_apply_for_selected_uuids(stage, model_name, action, uuids):
    """
    Task para incializar uma classe Differ do modelo: `model_name` e achama o metodo: apply_diff_record
    """
    logger.info(u"iniciando task_differ_apply_for_selected_uuids(stage: %s, model_name: %s, action: %s) para %s uuids" % (
        stage, model_name, action, len(uuids)))
    diff_class = None

    if model_name not in MODEL_NAME_LIST:
        raise ValueError(u'Param: model_name:%s com valor inesperado!' % model_name)
    else:
        logger.info(u"[%s][%s] Coletando: ADD para o modelo" % (stage, model_name))

    diff_class = DIFFERS[model_name]
    diff_class_instance = diff_class()
    for target_uuid in uuids:
        diff_class_instance.apply_diff_record(stage, action, target_uuid)


def enqueue_differ_consumer_tasks(stage='all', model_name='all', action='all'):
    logger.info(u"iniciando task_differ_apply_for_stage (stage: %s, model_name: %s, action: %s)" % (
        stage, model_name, action))
    diff_class = None
    r_queues = RQueues()
    get_db_connection()

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

    for stage_ in stages_list:
        for model_ in models_list:
            for action_ in actions_list:
                diff_class = DIFFERS[model_]
                diff_class_instance = diff_class()
                full_uuids_to_process = diff_class_instance.get_uuids_unapplied(stage, action)
                list_of_list_of_uuids = list(chunks(full_uuids_to_process, 1000))
                for list_of_uuids in list_of_list_of_uuids:
                    list_of_uuids_flat = [str(uuid) for uuid in list_of_uuids]
                    logger.info(u'enfilerando: task_differ_apply_for_selected_uuids(stage:%s, model: %s, action: %s)' % (stage_, model_, action_))
                    r_queues.enqueue(
                        'sync_ids', model_,
                        task_differ_apply_for_selected_uuids,
                        stage_, model_, action_, list_of_uuids_flat
                    )
                    create_sync_event_record(
                        'sync_ids', model_, 'task_differ_apply_for_selected_uuids',
                        u'Enfilerando task para consumir registros diff: stage %s model: %s: action: %s, quantidade de UUIDS: %s' % (
                            stage_, model_, action_, len(list_of_uuids_flat))
                    )
