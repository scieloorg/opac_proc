# coding: utf-8
import sys
from opac_proc.source_sync.utils import MODEL_NAME_LIST
from opac_proc.differs.utils import (
    ETL_STAGE_LIST,
    ETL_MODEL_NAME_LIST,
    ACTION_LIST
)


def clean_idsync_scheduler_params(model_name):
    """
    Valida que o parametro: model_name seja valido.
    Valores válidos são: 'all' ou os itens da lista
    MODEL_NAME_LIST.

    Quando o model_name é valido, retorna o valor esperado
    Quando não, executa um sys.exit com a mensagem do
    erro para o usuário
    """
    models_selected = []
    if model_name == 'all':
        models_selected = MODEL_NAME_LIST
    elif model_name not in MODEL_NAME_LIST:
        model_options = str(['all'] + MODEL_NAME_LIST)
        sys.exit(u'Modelo "%s" inválido. Opções: "all",%s ' % model_name, model_options)
    else:
        models_selected = [model_name, ]
    return models_selected


def clean_differ_scheduler_params(stage, model_name, action):
    """
    Valida que os parametros: stage, model_name, action sejam validos.
    Valores válidos são: 'all' ou os itens da lista
    ETL_STAGE_LIST, MODEL_NAME_LIST e ACTION_LIST respectivamente.

    Quando um parametro é valido, retorna o valor esperado
    Quando não, executa um sys.exit com a mensagem do
    erro para o usuário
    """

    if stage == 'all':
        stages_list = ETL_STAGE_LIST
    elif stage not in ETL_STAGE_LIST:
        sys.exit('Param: stage: %s com valor inesperado!' % stage)
    else:
        stages_list = [stage, ]

    if model_name == 'all':
        models_list = ETL_MODEL_NAME_LIST
    elif model_name not in ETL_MODEL_NAME_LIST:
        sys.exit('Param: model: %s com valor inesperado!' % model_name)
    else:
        models_list = [model_name]

    if action == 'all':
        actions_list = ACTION_LIST
    elif action not in ACTION_LIST:
        sys.exit('Param: action: %s com valor inesperado!' % action)
    else:
        actions_list = [action, ]

    return (stages_list, models_list, actions_list)
