# coding: utf-8
import os
import sys
import logging
import logging.config

import click

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.source_sync.utils import MODEL_NAME_LIST, STAGE_LIST, ACTION_LIST
from opac_proc.source_sync.populate_jobs import enqueue_full_populate_task_by_model
from opac_proc.source_sync.ids_data_retriever_jobs import (
    enqueue_ids_data_retriever,
    serial_run_ids_data_retriever
)

from opac_proc.source_sync.differ_producer_jobs import enqueue_differ_producer_tasks
from opac_proc.source_sync.differ_consumer_jobs import enqueue_differ_consumer_tasks
from opac_proc.source_sync.cleaner import (
    task_clean_diff_models,
    task_clean_id_models,
    task_clean_etl_models_by_stage,
)

logger = logging.getLogger(__name__)
logger_ini = os.path.join(os.path.dirname(__file__), 'logging.ini')
logging.config.fileConfig(logger_ini, disable_existing_loggers=False)

STAGE_LIST_STR = ', '.join(STAGE_LIST)
MODEL_NAME_LIST_STR = ', '.join(MODEL_NAME_LIST)
ACTION_LIST_STR = ', '.join(ACTION_LIST)

# ------------------------------------------------------ #
#                    DIFFER                              #
# ------------------------------------------------------ #


@click.group()
def differ():
    pass


@differ.command()
@click.option('--stage', default='all', help='Stage to produce. Options: all, %s.' % STAGE_LIST_STR)
@click.option('--model', default='all', help='Model to produce. Options: all, %s.' % MODEL_NAME_LIST_STR)
@click.option('--action', default='all', help='Action to produce. Options: all, %s' % ACTION_LIST_STR)
def differ_produce_records(stage, model, action):
    """Enfilera as tasks para gerar registros Differ do stage, modelo e action indicados"""
    enqueue_differ_producer_tasks(stage, model, action)


@differ.command()
@click.option('--stage', default='all', help='Stage to consume. Options: all, %s.' % STAGE_LIST_STR)
@click.option('--model', default='all', help='Model to consume. Options: all, %s.' % MODEL_NAME_LIST_STR)
@click.option('--action', default='all', help='Action to consume. Options: all, %s' % ACTION_LIST_STR)
def differ_consumer_tasks(stage, model, action):
    """Enfilera as tasks para processar registros Differ do stage, modelo e action indicados"""
    enqueue_differ_consumer_tasks(stage, model, action)


# ------------------------------------------------------ #
#                    CLEANER                             #
# ------------------------------------------------------ #


@click.group()
def cleaner():
    pass


@cleaner.command()
@click.option('--stage', default='all', help='Stage used to filter the Diff Model to delete. Options: all, %s.' % STAGE_LIST_STR)
@click.option('--model', default='all', help='DiffModel that you want to delete. Options: all, %s.' % MODEL_NAME_LIST_STR)
@click.option('--action', default='all', help='Action used to filter the Diff Model to delete. Options: all, %s' % ACTION_LIST_STR)
def clean_diff_models(stage, model, action):
    """Enfilera as tasks para remover registros Differ do stage, modelo e action indicados"""
    task_clean_diff_models(stage, model, action)


@cleaner.command()
@click.option('--model', default='all', help='IdModel to delete. Options: all, %s.' % MODEL_NAME_LIST_STR)
def clean_id_models(model):
    """Enfilera as tasks para remover registros de Ids do modelo indicado"""
    task_clean_id_models(model)


@cleaner.command()
@click.option('--stage', default='all', help='Stage used to filter the ETL Model to delete. Options: all, %s.' % STAGE_LIST_STR)
@click.option('--model', default='all', help='ETL model to delete. Options: all, %s.' % MODEL_NAME_LIST_STR)
def clean_etl_models(stage, model):
    """Enfilera as tasks para remover registros da fase Extracts do modelo indicado"""
    task_clean_etl_models_by_stage(stage, model)


# ------------------------------------------------------ #
#                    RETRIEVER                           #
# ------------------------------------------------------ #


@click.group()
def retriever():
    pass


@retriever.command()
@click.option('--model', default='all', help='DiffModel that you want to delete. Options: all, %s.' % MODEL_NAME_LIST_STR)
def retriever_enqueue(model):
    """ Enfilera as tasks necessárias para obter os IdModels do model indicado"""
    enqueue_ids_data_retriever(model)


@retriever.command()
@click.option('--model', default='all', help='DiffModel that you want to delete. Options: all, %s.' % MODEL_NAME_LIST_STR)
def retriever_serial(model):
    """ Roda o processo SERIAL necessário para obter os IdModels do model indicado"""
    serial_run_ids_data_retriever(model)


# ------------------------------------------------------ #
#                    POPULATE                            #
# ------------------------------------------------------ #


@click.group()
def populate():
    pass


@populate.command()
@click.option('--model', default='all', help='DiffModel to populate with ETL timestamps. Options: all, %s.' % MODEL_NAME_LIST_STR)
def populate_id_model(model):
    """ Enfilera as tasks necessárias para obter os IdModels do stage e model indicados"""
    enqueue_full_populate_task_by_model(model)


cli = click.CommandCollection(sources=[differ, cleaner, retriever, populate])


if __name__ == '__main__':
    cli()
