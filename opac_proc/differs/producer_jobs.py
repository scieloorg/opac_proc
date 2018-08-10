# coding: utf-8
import os
from datetime import datetime, timedelta
import logging
import logging.config

from opac_proc.web.config import DEFAULT_DIFF_SPAN
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.source_sync.utils import chunks
from .utils import (
    ETL_DIFFERS_BY_MODEL,
    ETL_MODEL_NAME_LIST,
    ETL_STAGE_LIST,
    ACTION_LIST,
    DIFF_MODEL_CLASS_BY_NAME
)

logger = logging.getLogger(__name__)
logger_ini = os.path.join(os.path.dirname(__file__), 'logging.ini')
logging.config.fileConfig(logger_ini, disable_existing_loggers=False)


# --------------------------------------------------- #
#                   ETL MODELS                        #
# --------------------------------------------------- #


def task_produce_diff_add(stage, model_name):
    if stage not in ETL_STAGE_LIST:
        raise ValueError(u'param stage: %s é inválido' % stage)
    if model_name not in ETL_MODEL_NAME_LIST:
        raise ValueError(u'param model_name: %s é inválido' % model_name)

    diff_class = ETL_DIFFERS_BY_MODEL[model_name]
    diff_class_instance = diff_class()
    uuids_to_add = diff_class_instance.collect_add_records(stage)
    logger.info(u'[%s][%s] %s uuids para adicionar', stage, model_name,
                len(uuids_to_add))

    for uuid in uuids_to_add:
        diff_class_instance.create_diff_model(stage, 'add', uuid)


def task_produce_diff_update(stage, model_name, since_date=None):
    if stage not in ETL_STAGE_LIST:
        raise ValueError(u'param stage: %s é inválido' % stage)
    if model_name not in ETL_MODEL_NAME_LIST:
        raise ValueError(u'param model_name: %s é inválido' % model_name)
    if since_date is None:
        since_date = datetime.today() - timedelta(days=DEFAULT_DIFF_SPAN)

    diff_class = ETL_DIFFERS_BY_MODEL[model_name]
    diff_class_instance = diff_class()
    uuids_to_update = diff_class_instance.collect_update_records(stage, since_date)
    logger.info(u'[%s][%s] %s uuids para atualizar (corte: %s)', stage, model_name,
                len(uuids_to_update), since_date)
    for uuid in uuids_to_update:
        diff_class_instance.create_diff_model(stage, 'update', uuid)


def task_produce_diff_delete(stage, model_name):
    if stage not in ETL_STAGE_LIST:
        raise ValueError(u'param stage: %s é inválido' % stage)
    if model_name not in ETL_MODEL_NAME_LIST:
        raise ValueError(u'param model_name: %s é inválido' % model_name)

    diff_class = ETL_DIFFERS_BY_MODEL[model_name]
    diff_class_instance = diff_class()
    uuids_to_delete = diff_class_instance.collect_delete_records(stage)
    logger.info(u'[%s][%s] %s uuids para remover', stage, model_name,
                len(uuids_to_delete))
    for uuid in uuids_to_delete:
        diff_class_instance.create_diff_model(stage, 'delete', uuid)


def task_delete_selected_diff_etl_model(stage, model_name, action, selected_uuids):
    if stage not in ETL_STAGE_LIST:
        raise ValueError(u'param stage: %s é inválido' % stage)
    if model_name not in ETL_MODEL_NAME_LIST:
        raise ValueError(u'param model_name: %s é inválido' % model_name)
    if action not in ACTION_LIST:
        raise ValueError(u'param action: %s é inválido' % action)

    get_db_connection()
    model_class = DIFF_MODEL_CLASS_BY_NAME[model_name]
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_uuids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(
                'sync_ids',
                model_name,
                task_delete_selected_diff_etl_model,
                stage, model_name, action, uuid_as_string_list)  # args da task
    else:
        documents_to_delete = model_class.objects.filter(uuid__in=selected_uuids)
        documents_to_delete.delete()


def task_delete_all_diff_etl_model(stage, model_name, action):
    get_db_connection()
    if stage not in ETL_STAGE_LIST:
        raise ValueError(u'param stage: %s é inválido' % stage)
    if model_name not in ETL_MODEL_NAME_LIST:
        raise ValueError(u'param model_name: %s é inválido' % model_name)
    if action not in ACTION_LIST:
        raise ValueError(u'param action: %s é inválido' % action)

    model_class = DIFF_MODEL_CLASS_BY_NAME[model_name]
    diff_records = model_class.objects.filter(stage=stage, action=action)
    diff_records.delete()
