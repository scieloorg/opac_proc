# coding: utf-8
import os
import sys
import logging
import logging.config

import click

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.differs.producer_jobs import (
    task_produce_diff_add,
    task_produce_diff_update,
    task_produce_diff_delete,
    task_delete_all_diff_etl_model
)
from opac_proc.differs.consumer_jobs import (
    task_consume_diff_add,
    task_consume_diff_update,
    task_consume_diff_delete,
)

from opac_proc.differs.utils import (
    ETL_STAGE_LIST,
    ETL_MODEL_NAME_LIST,
    ACTION_LIST
)

logger = logging.getLogger(__name__)
logger_ini = os.path.join(os.path.dirname(__file__), 'logging.ini')
logging.config.fileConfig(logger_ini, disable_existing_loggers=False)

STAGE_LIST_STR = ', '.join(ETL_STAGE_LIST)
MODEL_NAME_LIST_STR = ', '.join(ETL_MODEL_NAME_LIST)
ACTION_LIST_STR = ', '.join(ACTION_LIST)


@click.group()
def differ():
    pass


@differ.command()
@click.option('--stage', default='all', help='Stage to produce diff records. Options: all, %s.' % STAGE_LIST_STR)
@click.option('--model', default='all', help='Model to produce diff records. Options: all, %s.' % MODEL_NAME_LIST_STR)
@click.option('--action', default='all', help='Action to produce diff records. Options: all, %s' % ACTION_LIST_STR)
def produce(stage, model, action):
    """
    Enfilera as tasks para GERAR registros Differ do stage, modelo e action
    indicados
    """

    if stage == 'all':
        stages_list = ETL_STAGE_LIST
    elif stage not in ETL_STAGE_LIST:
        raise ValueError('Param: stage: %s com valor inesperado!' % stage)
    else:
        stages_list = [stage, ]

    if model == 'all':
        models_list = ETL_MODEL_NAME_LIST
    elif model not in ETL_MODEL_NAME_LIST:
        raise ValueError('Param: model: %s com valor inesperado!' % model)
    else:
        models_list = [model]

    if action == 'all':
        actions_list = ACTION_LIST
    elif action not in ACTION_LIST:
        raise ValueError('Param: action: %s com valor inesperado!' % action)
    else:
        actions_list = [action, ]

    r_queues = RQueues()
    task_fn_by_action = {
        'add': task_produce_diff_add,
        'update': task_produce_diff_update,
        'delete': task_produce_diff_delete,
    }

    for stage_ in stages_list:
        for model_ in models_list:
            for action_ in actions_list:
                task_fn = task_fn_by_action[action_]
                logger.info("[%s][%s][%s] enfilerando para producir registros diff", stage_, model_, action_)
                r_queues.enqueue('sync_ids', model_, task_fn, stage_, model_)


@differ.command()
@click.option('--stage', default='all', help='Stage to consume diff records. Options: all, %s.' % STAGE_LIST_STR)
@click.option('--model', default='all', help='Model to consume diff records. Options: all, %s.' % MODEL_NAME_LIST_STR)
@click.option('--action', default='all', help='Action to consume diff records. Options: all, %s' % ACTION_LIST_STR)
def consume(stage, model, action):
    """
    Enfilera as tasks para GERAR registros Differ do stage, modelo e action
    indicados
    """

    if stage == 'all':
        stages_list = ETL_STAGE_LIST
    elif stage not in ETL_STAGE_LIST:
        raise ValueError('Param: stage: %s com valor inesperado!' % stage)
    else:
        stages_list = [stage, ]

    if model == 'all':
        models_list = ETL_MODEL_NAME_LIST
    elif model not in ETL_MODEL_NAME_LIST:
        raise ValueError('Param: model: %s com valor inesperado!' % model)
    else:
        models_list = [model]

    if action == 'all':
        actions_list = ACTION_LIST
    elif action not in ACTION_LIST:
        raise ValueError('Param: action: %s com valor inesperado!' % action)
    else:
        actions_list = [action, ]

    r_queues = RQueues()
    task_fn_by_action = {
        'add': task_consume_diff_add,
        'update': task_consume_diff_update,
        'delete': task_consume_diff_delete,
    }

    for stage_ in stages_list:
        for model_ in models_list:
            for action_ in actions_list:
                task_fn = task_fn_by_action[action_]
                logger.info("[%s][%s][%s] enfilerando para producir registros diff", stage_, model_, action_)
                r_queues.enqueue('sync_ids', model_, task_fn, stage_, model_)


@differ.command()
@click.option('--stage', default='all', help='Stage to produce. Options: all, %s.' % STAGE_LIST_STR)
@click.option('--model', default='all', help='Model to produce. Options: all, %s.' % MODEL_NAME_LIST_STR)
@click.option('--action', default='all', help='Action to produce. Options: all, %s' % ACTION_LIST_STR)
def remove(stage, model, action):
    """
    Enfilera as tasks para gerar CONSUMIR registros Differ do stage, modelo e
    action indicados
    """

    if stage == 'all':
        stages_list = ETL_STAGE_LIST
    elif stage not in ETL_STAGE_LIST:
        raise ValueError('Param: stage: %s com valor inesperado!' % stage)
    else:
        stages_list = [stage, ]

    if model == 'all':
        models_list = ETL_MODEL_NAME_LIST
    elif model not in ETL_MODEL_NAME_LIST:
        raise ValueError('Param: model: %s com valor inesperado!' % stage)
    else:
        models_list = [model]

    if action == 'all':
        actions_list = ACTION_LIST
    elif model not in ACTION_LIST:
        raise ValueError('Param: model: %s com valor inesperado!' % stage)
    else:
        actions_list = [action, ]

    r_queues = RQueues()
    for stage_ in stages_list:
        for model_ in models_list:
            for action_ in actions_list:
                logger.info("[%s][%s][%s] enfilerando para remover registros diff", stage_, model_, action_)
                r_queues.enqueue(
                    'sync_ids',
                    model_,
                    task_delete_all_diff_etl_model, stage_, model_, action_)


cli = click.CommandCollection(sources=[differ])


if __name__ == '__main__':
    cli()
