# coding: utf-8
import os
import logging
import logging.config

from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.source_sync.utils import chunks
from .utils import (
    ETL_DIFFERS_BY_MODEL,
    ETL_MODEL_NAME_LIST,
    ETL_STAGE_LIST,
)

logger = logging.getLogger(__name__)
logger_ini = os.path.join(os.path.dirname(__file__), 'logging.ini')
logging.config.fileConfig(logger_ini, disable_existing_loggers=False)


# --------------------------------------------------- #
#                   ETL MODELS                        #
# --------------------------------------------------- #


def task_differ_apply_for_selected_uuids(stage, model_name, action, uuids):
    """
    Task para incializar uma classe Differ do modelo: `model_name` e
    chama o metodo: apply_diff_record para aplicar a instrução do registro diff.
    """

    if stage not in ETL_STAGE_LIST:
        raise ValueError(u'param stage: %s é inválido' % stage)

    if model_name not in ETL_MODEL_NAME_LIST:
        raise ValueError(u'Param: model_name:%s com valor inesperado!' % model_name)

    logger.info(
        u"[%s][%s] consumindo registros DIFF: %s para o modelo para %s UUIDs",
        stage, model_name, action, len(uuids))

    diff_class = ETL_DIFFERS_BY_MODEL[model_name]
    diff_class_instance = diff_class()
    diff_class_instance.apply_diff_record(stage, action, uuids)


def task_consume_diff_add(stage, model_name):
    """
    Task que consume os registros ADD dos diff filtrando pelos parametros:
    - @param stage: fase do ETL
    - @param model_name: nome do modelo ETL
    """

    if stage not in ETL_STAGE_LIST:
        raise ValueError(u'param stage: %s é inválido' % stage)

    if model_name not in ETL_MODEL_NAME_LIST:
        raise ValueError(u'param model_name: %s é inválido' % model_name)

    action = 'add'
    SLICE_SIZE = 1000
    r_queues = RQueues()
    get_db_connection()
    diff_class = ETL_DIFFERS_BY_MODEL[model_name]
    diff_class_instance = diff_class()
    full_uuids_to_process = diff_class_instance.get_uuids_unapplied(stage, action)
    list_of_list_of_uuids = list(chunks(full_uuids_to_process, SLICE_SIZE))

    for list_of_uuids in list_of_list_of_uuids:
        list_of_uuids_flat = [str(uuid) for uuid in list_of_uuids]
        logger.info(u'enfilerando: consumo de UUUIDs selecionados (stage:%s, model: %s, action: %s)' % (stage, model_name, action))
        r_queues.enqueue(
            'sync_ids', model_name,
            task_differ_apply_for_selected_uuids,
            stage, model_name, action, list_of_uuids_flat)


def task_consume_diff_update(stage, model_name):
    """
    Task que consume os registros UPDATE dos diff filtrando pelos parametros:
    - @param stage: fase do ETL
    - @param model_name: nome do modelo ETL
    """

    if stage not in ETL_STAGE_LIST:
        raise ValueError(u'param stage: %s é inválido' % stage)

    if model_name not in ETL_MODEL_NAME_LIST:
        raise ValueError(u'param model_name: %s é inválido' % model_name)

    action = 'update'
    SLICE_SIZE = 1000
    r_queues = RQueues()
    get_db_connection()
    diff_class = ETL_DIFFERS_BY_MODEL[model_name]
    diff_class_instance = diff_class()
    full_uuids_to_process = diff_class_instance.get_uuids_unapplied(stage, action)
    list_of_list_of_uuids = list(chunks(full_uuids_to_process, SLICE_SIZE))

    for list_of_uuids in list_of_list_of_uuids:
        list_of_uuids_flat = [str(uuid) for uuid in list_of_uuids]
        logger.info(u'enfilerando: consumo de UUUIDs selecionados (stage:%s, model: %s, action: %s)' % (stage, model_name, action))
        r_queues.enqueue(
            'sync_ids', model_name,
            task_differ_apply_for_selected_uuids,
            stage, model_name, action, list_of_uuids_flat)


def task_consume_diff_delete(stage, model_name):
    """
    Task que consume os registros DELETE dos diff filtrando pelos parametros:
    - @param stage: fase do ETL
    - @param model_name: nome do modelo ETL
    """

    if stage not in ETL_STAGE_LIST:
        raise ValueError(u'param stage: %s é inválido' % stage)

    if model_name not in ETL_MODEL_NAME_LIST:
        raise ValueError(u'param model_name: %s é inválido' % model_name)

    action = 'delete'
    SLICE_SIZE = 1000
    r_queues = RQueues()
    get_db_connection()
    diff_class = ETL_DIFFERS_BY_MODEL[model_name]
    diff_class_instance = diff_class()
    full_uuids_to_process = diff_class_instance.get_uuids_unapplied(stage, action)
    list_of_list_of_uuids = list(chunks(full_uuids_to_process, SLICE_SIZE))

    for list_of_uuids in list_of_list_of_uuids:
        list_of_uuids_flat = [str(uuid) for uuid in list_of_uuids]
        logger.info(u'enfilerando: consumo de UUUIDs selecionados (stage:%s, model: %s, action: %s)' % (stage, model_name, action))
        r_queues.enqueue(
            'sync_ids', model_name,
            task_differ_apply_for_selected_uuids,
            stage, model_name, action, list_of_uuids_flat)
