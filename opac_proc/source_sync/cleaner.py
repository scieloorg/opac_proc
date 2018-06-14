# coding: utf-8
import os
import sys
import logging
import logging.config

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.datastore import identifiers_models
from opac_proc.datastore import diff_models
from opac_proc.datastore import models
from opac_proc.source_sync.utils import MODEL_NAME_LIST, STAGE_LIST, ACTION_LIST
from opac_proc.source_sync.event_logger import create_sync_event_record

logger = logging.getLogger(__name__)
logger_ini = os.path.join(os.path.dirname(__file__), 'logging.ini')
logging.config.fileConfig(logger_ini, disable_existing_loggers=False)


DIFF_MODEL_CLASS = {
    'collection': diff_models.CollectionDiffModel,
    'journal': diff_models.JournalDiffModel,
    'issue': diff_models.IssueDiffModel,
    'article': diff_models.ArticleDiffModel,
    'news': diff_models.NewsDiffModel,
    'press_release': diff_models.PressReleaseDiffModel
}


ID_MODEL_CLASS = {
    'collection': identifiers_models.CollectionIdModel,
    'journal': identifiers_models.JournalIdModel,
    'issue': identifiers_models.IssueIdModel,
    'article': identifiers_models.ArticleIdModel,
    'news': identifiers_models.NewsIdModel,
    'press_release': identifiers_models.PressReleaseIdModel
}

MODEL_CLASS_BY_STAGE = {
    'extract': {
        'collection': models.ExtractCollection,
        'journal': models.ExtractJournal,
        'issue': models.ExtractIssue,
        'article': models.ExtractArticle,
        'news': models.ExtractNews,
        'press_release': models.ExtractPressRelease
    },
    'transform': {
        'collection': models.TransformCollection,
        'journal': models.TransformJournal,
        'issue': models.TransformIssue,
        'article': models.TransformArticle,
        'news': models.TransformNews,
        'press_release': models.TransformPressRelease
    },
    'load': {
        'collection': models.LoadCollection,
        'journal': models.LoadJournal,
        'issue': models.LoadIssue,
        'article': models.LoadArticle,
        'news': models.LoadNews,
        'press_release': models.LoadPressRelease
    }
}


def delete_identifiers(model_name):
    """função que remove documentos (modelos Identifiers*) para o modelo: `model_name`"""
    if model_name not in ID_MODEL_CLASS.keys():
        raise ValueError(u'parametro: model_name: %s não é válido!' % model_name)
    get_db_connection()
    model_class = ID_MODEL_CLASS[model_name]
    objects = model_class.objects()
    logger.info(u"Removendo: %s objetos do modelo: %s" % (objects.count(), model_name))
    objects.delete()
    logger.info(u"Objetos removidos com sucesso!")


def delete_diff_models(stage, model_name, action):
    """função que remove documentos (modelos Diff*) para o modelo: `model_name`"""

    if stage not in STAGE_LIST:
        raise ValueError(u'parametro: stage: %s não é válido!' % stage)

    if model_name not in DIFF_MODEL_CLASS.keys():
        raise ValueError(u'parametro: model_name: %s não é válido!' % model_name)

    if action not in ACTION_LIST:
        raise ValueError(u'parametro: action: %s não é válido!' % action)

    get_db_connection()
    model_class = DIFF_MODEL_CLASS[model_name]
    objects = model_class.objects.filter(stage=stage, action=action)
    logger.info(u"Removendo: %s objetos do modelo: %s" % (objects.count(), model_name))
    objects.delete()
    logger.info(u"Objetos removidos com sucesso!")


def delete_etl_models(stage, model_name):
    """função que remove documentos (modelos Diff*) para o modelo: `model_name`"""

    if stage not in STAGE_LIST:
        raise ValueError(u'parametro: stage: %s não é válido!' % stage)

    if model_name not in MODEL_CLASS_BY_STAGE[stage].keys():
        raise ValueError(u'parametro: model_name: %s não é válido!' % model_name)

    get_db_connection()
    model_class = MODEL_CLASS_BY_STAGE[stage][model_name]
    objects = model_class.objects.all()
    logger.info(u"Removendo: %s objetos do modelo: %s" % (objects.count(), model_name))
    objects.delete()
    logger.info(u"Objetos removidos com sucesso!")


def task_clean_diff_models(stage='all', model_name='all', action='all'):
    """
    task que enfilera funções para remover modelos Diffs.
    Param:
    - `stage`: filtro do campo stage: "extract", "transform" ou "load"
    - `model_name`: modelo a ser removido: "collection", "journal", etc.
    - `action` filtro do campo: "add" | "update" | "delete"
    """
    r_queues = RQueues()

    if model_name == 'all':
        model_name_list = DIFF_MODEL_CLASS.keys()
    else:
        model_name_list = [model_name]

    if stage == 'all':
        stages_list = STAGE_LIST
    else:
        stages_list = [stage, ]

    if action == 'all':
        actions_list = ACTION_LIST
    else:
        actions_list = [action, ]

    for model_ in model_name_list:
        for stage_ in stages_list:
            for action_ in actions_list:
                msg = u'Enfilerando task para remover o diff model, modelo: %s, stage: %s, action: %s' % (model_, stage_, action_)
                logger.info(msg)
                create_sync_event_record('sync_ids', model_, 'delete_diff_models', msg)
                r_queues.enqueue('sync_ids', model_, delete_diff_models, stage_, model_, action_)
                msg = u'Fim: Enfilerando task para remover o diff model, modelo: %s, stage: %s, action: %s' % (model_, stage_, action_)
                logger.info(msg)
                create_sync_event_record('sync_ids', model_, 'delete_diff_models', msg)


def task_clean_id_models(model_name='all'):
    """
    task que enfilera funções para remover modelos Identifiers.
    Param:
    - `model_name`: modelo a ser removido: "collection", "journal", etc.
    """
    r_queues = RQueues()
    if model_name == 'all':
        model_name_list = ID_MODEL_CLASS.keys()
    else:
        model_name_list = [model_name]

    for model_name_ in model_name_list:
        msg = u'Enfilerando task para remover o id model, modelo: %s' % model_name_
        logger.info(msg)
        create_sync_event_record('sync_ids', model_name_, 'delete_identifiers', msg)
        r_queues.enqueue('sync_ids', model_name_, delete_identifiers, model_name_)
        msg = u'Fim: Enfilerando task para remover o id model, modelo: %s' % model_name_
        logger.info(msg)
        create_sync_event_record('sync_ids', model_name_, 'delete_identifiers', msg)


def task_clean_etl_models_by_stage(stage='all', model_name='all'):
    """
    task que enfilera funções para remover modelos da fase (stage) indicada.
    Param:
    - `model_name`: modelo a ser removido: "collection", "journal", etc.
    """
    r_queues = RQueues()
    if stage == 'all':
        stages_list = STAGE_LIST
    else:
        stages_list = [stage, ]

    if model_name == 'all':
        model_name_list = ID_MODEL_CLASS.keys()
    else:
        model_name_list = [model_name]

    for model_name_ in model_name_list:
        for stage_ in stages_list:
            msg = u'Enfilerando task para remover o modelo: %s da stage: %s' % (model_name_, stage_)
            logger.info(msg)
            create_sync_event_record('sync_ids', model_name_, 'delete_identifiers', msg)

            r_queues.enqueue('sync_ids', model_name_, delete_etl_models, stage_, model_name_)

            msg = u'Fim: Enfilerando task para remover o modelo: %s da stage: %s' % (model_name_, stage_)
            logger.info(msg)
            create_sync_event_record('sync_ids', model_name_, 'delete_identifiers', msg)
