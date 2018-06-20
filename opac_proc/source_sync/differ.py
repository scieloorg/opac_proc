# coding: utf-8
import sys
import os
import logging
import logging.config

from datetime import datetime, timedelta

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.datastore import models as proc_models
from opac_proc.datastore import identifiers_models as id_models
from opac_proc.datastore import diff_models as diff_models
from opac_proc.web import config
from opac_proc.source_sync.utils import (
    MODEL_NAME_LIST,
    STAGE_LIST,
    ACTION_LIST,
    parse_journal_issn_from_issue_code,
    parse_journal_issn_from_article_code,
    parse_issue_pid_from_article_code,
    parse_date_str_to_datetime_obj,
)
from opac_proc.extractors.process import (
    ProcessExtractCollection,
    ProcessExtractJournal,
    ProcessExtractIssue,
    ProcessExtractArticle,
    ProcessExtractPressRelease,
    ProcessExtractNews
)
from opac_proc.transformers.process import (
    ProcessTransformCollection,
    ProcessTransformJournal,
    ProcessTransformIssue,
    ProcessTransformArticle,
    ProcessTransformPressRelease,
    ProcessTransformNews
)
from opac_proc.loaders.process import (
    ProcessLoadCollection,
    ProcessLoadJournal,
    ProcessLoadIssue,
    ProcessLoadArticle,
    ProcessLoadPressRelease,
    ProcessLoadNews
)

logger = logging.getLogger(__name__)
logger_ini = os.path.join(os.path.dirname(__file__), 'logging.ini')
logging.config.fileConfig(logger_ini, disable_existing_loggers=False)


DIFF_APPLY_PROCESSORS = {
    'add': {
        'extract': {
            'collection': ProcessExtractCollection,
            'journal': ProcessExtractJournal,
            'issue': ProcessExtractIssue,
            'article': ProcessExtractArticle,
            'news': ProcessExtractNews,
            'press_release': ProcessExtractPressRelease,
        },
        'transform': {
            'collection': ProcessTransformCollection,
            'journal': ProcessTransformJournal,
            'issue': ProcessTransformIssue,
            'article': ProcessTransformArticle,
            'news': ProcessTransformNews,
            'press_release': ProcessTransformPressRelease,
        },
        'load': {
            'collection': ProcessLoadCollection,
            'journal': ProcessLoadJournal,
            'issue': ProcessLoadIssue,
            'article': ProcessLoadArticle,
            'news': ProcessLoadPressRelease,
            'press_release': ProcessLoadNews,
        }
    },
    'update': {
        'extract': {
            'collection': ProcessExtractCollection,
            'journal': ProcessExtractJournal,
            'issue': ProcessExtractIssue,
            'article': ProcessExtractArticle,
            'news': ProcessExtractNews,
            'press_release': ProcessExtractPressRelease,
        },
        'transform': {
            'collection': ProcessTransformCollection,
            'journal': ProcessTransformJournal,
            'issue': ProcessTransformIssue,
            'article': ProcessTransformArticle,
            'news': ProcessTransformNews,
            'press_release': ProcessTransformPressRelease,
        },
        'load': {
            'collection': ProcessLoadCollection,
            'journal': ProcessLoadJournal,
            'issue': ProcessLoadIssue,
            'article': ProcessLoadArticle,
            'news': ProcessLoadNews,
            'press_release': ProcessLoadPressRelease,
        }
    },
    'delete': {

    }
}


class DifferBase(object):
    collection_acronym = config.OPAC_PROC_COLLECTION
    _db = None
    model_name = None
    # proc models
    ex_model_class = None
    tr_model_class = None
    lo_model_class = None
    # identifiers models
    id_model_class = None
    # diff models
    diff_model_class = None

    def __init__(self):
        if self.model_name is None:
            raise AttributeError(u'Falta definir atributo: model_name')

        if self.ex_model_class is None:
            raise AttributeError(u'Falta definir atributo: ex_model_class')

        if self.tr_model_class is None:
            raise AttributeError(u'Falta definir atributo: tr_model_class')

        if self.lo_model_class is None:
            raise AttributeError(u'Falta definir atributo: lo_model_class')

        if self.id_model_class is None:
            raise AttributeError(u'Falta definir atributo: id_model_class')

        if self.diff_model_class is None:
            raise AttributeError(u'Falta definir atributo: diff_model_class')

        if self._db is None:
            self._db = get_db_connection()

        super(DifferBase, self).__init__()

    def _update_model_instance(self, model_class, obj_filter_dict, new_data_dict):
        """
        atualizo o registro no banco, buscando pelo "obj_filter_dict"
        e mudando os campos "new_data_dict"
        """
        obj = self._get_or_create_model_instance(model_class, obj_filter_dict)
        obj.modify(**new_data_dict)

    def _get_or_create_model_instance(self, model_class, model_selector_filter_dict):
        """
        consulta o banco usando os filtros definidos em: `model_selector_filter_dict`
        - caso existe um registro: retorna ele
        - caso não existe: cria um novo registro com os valores definidos em: `model_selector_filter_dict`
        """

        obj = model_class.objects.filter(**model_selector_filter_dict)

        if obj.count() == 0:
            new_obj = self.idmodel_class(**model_selector_filter_dict)
            new_obj.save()
            return new_obj
        elif obj.count() == 1:
            return obj.first()
        else:
            error_msg = u'Muitos documentos retornados (modelo: %s) com a query: %s' % (
                self.model_name, model_selector_filter_dict)
            raise Exception(error_msg)

    def has_id_retrieved(self, target_uuid):
        """
        Retorna True quando o documento com uuid: `target_uuid` do
        modelo `self.id_model_class` tem exatamente um registro salvo.
        Isso significa que o registro no IdentifierModel correspondente existe.
        """
        objs_count = self.id_model_class.objects.filter(uuid=target_uuid).count()
        return objs_count == 1

    def is_extracted(self, target_uuid):
        """
        Retorna True quando o documento com uuid: `target_uuid` do
        modelo `self.ex_model` tem exatamente um registro salvo.
        Isso significa que o registro no modelo Extract correspondente existe.
        """
        objs_count = self.ex_model_class.objects.filter(uuid=target_uuid).count()
        return objs_count == 1

    def is_transformed(self, target_uuid):
        """
        Retorna True quando o documento com uuid: `target_uuid` do
        modelo `self.tr_model` tem exatamente um registro salvo.
        Isso significa que o registro no modelo Transform correspondente existe.
        """
        objs_count = self.tr_model_class.objects.filter(uuid=target_uuid).count()
        return objs_count == 1

    def is_loaded(self, target_uuid):
        """
        Retorna True quando o documento com uuid: `target_uuid` do
        modelo `self.lo_model` tem exatamente um registro salvo.
        Isso significa que o registro no modelo Load correspondente existe.
        """
        objs_count = self.lo_model_class.objects.filter(uuid=target_uuid).count()
        return objs_count == 1

    def check_add_operation(self, stage, target_uuid):
        """
        params:
        - stage: 'extract' | 'transform' | 'load'
        - target_uuid: uuid do modelos que estamos analizando
        """

        if stage == 'extract':
            has_id_retrieved = self.has_id_retrieved(target_uuid)
            is_extracted = self.is_extracted(target_uuid)
            return has_id_retrieved and not is_extracted
        elif stage == 'transform':
            is_extracted = self.is_extracted(target_uuid)
            is_transformed = self.is_transformed(target_uuid)
            return is_extracted and not is_transformed
        elif stage == 'load':
            is_transformed = self.is_transformed(target_uuid)
            is_loaded = self.is_loaded(target_uuid)
            return is_transformed and not is_loaded
        else:
            raise ValueError(u'Parametro: "stage" inválido! Valores esperados: "extract" ou "transform" ou "load"!')

    def check_update_operation(self, stage, target_uuid):
        """
        params:
        - stage: 'extract' | 'transform' | 'load'
        - target_uuid: uuid do modelos que estamos analizando
        """

        if stage == 'extract':
            has_id_retrieved = self.has_id_retrieved(target_uuid)
            is_extracted = self.is_extracted(target_uuid)
            if has_id_retrieved and is_extracted:
                id_model_instance = self.id_model_class.objects.get(uuid=target_uuid)
                ex_model_instance = self.ex_model_class.objects.get(uuid=target_uuid)
                return id_model_instance.processing_date > ex_model_instance.metadata.updated_at
            else:
                return False
        elif stage == 'transform':
            is_extracted = self.is_extracted(target_uuid)
            is_transformed = self.is_transformed(target_uuid)
            if is_extracted and is_transformed:
                ex_model_instance = self.ex_model_class.objects.get(uuid=target_uuid)
                tr_model_instance = self.tr_model_class.objects.get(uuid=target_uuid)
                return ex_model_instance.metadata.updated_at > tr_model_instance.metadata.updated_at
            else:
                return False
        elif stage == 'load':
            is_transformed = self.is_transformed(target_uuid)
            is_loaded = self.is_loaded(target_uuid)
            if is_transformed and not is_loaded:
                tr_model_instance = self.tr_model_class.objects.get(uuid=target_uuid)
                lo_model_instance = self.lo_model_class.objects.get(uuid=target_uuid)
                return tr_model_instance.metadata.updated_at > lo_model_instance.metadata.updated_at
            else:
                return False
        else:
            raise ValueError(u'Parametro: "stage" inválido! Valores esperados: "extract" ou "transform" ou "load"!')

    def check_delete_operation(self, stage, target_uuid):
        """
        params:
        - stage: 'extract' | 'transform' | 'load'
        - target_uuid: uuid do modelos que estamos analizando
        """
        if stage == 'extract':
            has_id_retrieved = self.has_id_retrieved(target_uuid)
            is_extracted = self.is_extracted(target_uuid)
            return is_extracted and not has_id_retrieved
        elif stage == 'transform':
            is_extracted = self.is_extracted(target_uuid)
            is_transformed = self.is_transformed(target_uuid)
            return is_transformed and not is_extracted
        elif stage == 'load':
            is_transformed = self.is_transformed(target_uuid)
            is_loaded = self.is_loaded(target_uuid)
            return is_loaded and not is_transformed
        else:
            raise ValueError(u'Parametro: "stage" inválido! Valores esperados: "extract" ou "transform" ou "load"!')

    def collect_add_records(self, stage):
        """
        Params:
        - stage: a fase que queremos atualizar (adicionar novos registros): opções:
            - 'extract': quando queremos atualizar a lista de extraidos
            - 'transform': quando queremos atualizar a lista de transformados
            - 'load': quando queremos atualizar a lista de carregados

        Percorre os modelos
        Para cada modelo (`self.model_name`):
            verificamos se esse modelo: esta presente na fase anterior e não na fase: `stage`
            -> então é um candidado a ser ADICIONADO na fase : `stage`

        Resultado:
            retorna a lista de UUIDs que precisam ser addicionados na fase `stage`
        """
        if stage in STAGE_LIST:
            if stage == 'extract':
                extracted_uuids = self.ex_model_class.objects.all().values_list('uuid')
                return self.id_model_class.objects.filter(uuid__nin=extracted_uuids).values_list('uuid')
            elif stage == 'transform':
                transformed_uuids = self.tr_model_class.objects.all().values_list('uuid')
                return self.ex_model_class.objects.filter(uuid__nin=transformed_uuids).values_list('uuid')
            elif stage == 'load':
                loaded_uuids = self.lo_model_class.objects.all().values_list('uuid')
                return self.tr_model_class.objects.filter(uuid__nin=loaded_uuids).values_list('uuid')
        else:
            raise ValueError(u'Parametro: "stage" inválido! Valores esperados: "extract" ou "transform" ou "load"!')

    def collect_update_records(self, stage, since_date=None):
        """
        Params:
        - stage: a fase que queremos atualizar (atualizar registros): opções:
            - 'extract': quando queremos atualizar a lista de extraidos
            - 'transform': quando queremos atualizar a lista de transformados
            - 'load': quando queremos atualizar a lista de carregados
        - since:
            A data para filtrar (default: None)
            Se o valor for None, procura por dados modificados nos últimos 7 dias

        Percorre os modelos de identificadores (self.id_model_class) com data de
        processamento de X dias para cá (segundo o param: since_date, por padrão
        nos últimos 7 dias).
        Se entrar nesse critério, coletamos esse id para analizar com mais detalhe
        no próximo passo.

        Para cada UUID coletado anteriormente, filtramos esses UUID caso o resultado
        do metodo: self.check_update_operation seja True. Neste caso o UUID é
        incluido na lista de UUIDs resultantes.

        Resultado:
            retorna a lista de UUIDs que precisam ser addicionados na fase `stage`
        """
        if since_date is None:
            since_date = datetime.now() - timedelta(days=7)  # hoje - 7 dias
        elif not isinstance(since_date, datetime):
            raise ValueError(u'Param: since_date deve ser uma instânciade datetime')

        if stage in STAGE_LIST:
            # obtemos os UUID dos modelos identifiers que foram modificados recentemente
            recently_updated_uuids = self.id_model_class.objects(processing_date__gt=since_date).values_list('uuid')
            if stage == 'extract':
                traget_model_class = self.ex_model_class
            elif stage == 'transform':
                traget_model_class = self.tr_model_class
            elif stage == 'load':
                traget_model_class = self.lo_model_class

            if recently_updated_uuids:
                uuids = traget_model_class.objects(uuid__in=recently_updated_uuids).values_list('uuid')
                return [uuid for uuid in uuids if self.check_update_operation(stage, uuid)]
            else:
                return []
        else:
            raise ValueError(u'Parametro: "stage" inválido! Valores esperados: "extract" ou "transform" ou "load"!')

    def collect_delete_records(self, stage):
        """
        Params:
        - stage: a fase que queremos atualizar (remover registros): opções:
            - 'extract': quando queremos atualizar a lista de extraidos
            - 'transform': quando queremos atualizar a lista de transformados
            - 'load': quando queremos atualizar a lista de carregados

        Percorre os modelos (self.model_name):
        Para cada modelo (`self.model_name`):
            verificamos se esse modelo: esta presente na fase stage,  e NÃO esta na fase anterior
            -> então é um candidado a ser REMOVIDO na fase : `stage`

        Resultado:
            retorna a lista de UUIDs que precisam ser removidos na fase `stage`
        """
        if stage in STAGE_LIST:
            if stage == 'extract':
                identifiers_uuids = self.id_model_class.objects.all().values_list('uuid')
                return self.ex_model_class.objects.filter(uuid__nin=identifiers_uuids).values_list('uuid')
            elif stage == 'transform':
                extracted_uuids = self.ex_model_class.objects.all().values_list('uuid')
                return self.tr_model_class.objects.filter(uuid__nin=extracted_uuids).values_list('uuid')
            elif stage == 'load':
                transformed_uuids = self.tr_model_class.objects.all().values_list('uuid')
                return self.lo_model_class.objects.filter(uuid__nin=transformed_uuids).values_list('uuid')
        else:
            raise ValueError(u'Parametro: "stage" inválido! Valores esperados: "extract" ou "transform" ou "load"!')

    def get_model_class_to_collect_diff_data(self, stage, action):
        """
        Retorna a classe de modelo certa para fazer a consulta pelo UUID,
        e assim obter os campos com a info para criar o modelo do DiffModel
        """
        if stage == 'extract':
            if action == 'add':
                # para consultar o UUID a ser agregado no Extract. deve procurar no IdModel
                return self.id_model_class
            else:
                # para consultar o UUID a ser atualizado no Extract. deve procurar no Extract
                return self.ex_model_class
        elif stage == 'transform':
            if action == 'add':
                # para consultar o UUID a ser agregado no Extract. deve procurar no IdModel
                return self.ex_model_class
            else:
                # para consultar o UUID a ser atualizado no Extract. deve procurar no Extract
                return self.tr_model_class
        elif stage == 'load':
            if action == 'add':
                # para consultar o UUID a ser agregado no Extract. deve procurar no IdModel
                return self.tr_model_class
            else:
                # para consultar o UUID a ser atualizado no Extract. deve procurar no Extract
                return self.lo_model_class

    def create_diff_model(self, stage, action, target_uuid):

        doc_data = {
            'uuid': target_uuid,
            'stage': stage,
            'action': action,
        }

        if stage in STAGE_LIST:
            model_class = self.get_model_class_to_collect_diff_data(stage, action)
            model_instance = model_class.objects.get(uuid=target_uuid)
            diff_data = model_instance.get_diff_model_data
            doc_data.update(diff_data)
            # salvamos o registro de modelo Diff
            self.diff_model_class(**doc_data).save()
        else:
            raise ValueError(u'Parametro: "stage" inválido! Valores esperados: "extract" ou "transform" ou "load"!')

    def get_uuids_unapplied(self, stage, action):
        return self.diff_model_class.objects.filter(stage=stage, action=action, done_at=None).values_list('uuid')

    def apply_diff_record(self, stage, action, target_uuid):
        logger.info(
            "Aplicando o diff model para: stage: %s, action: %s, modelo: %s, UUID: %s" % (
                stage, action, self.model_name, target_uuid))
        # get processor
        processor_class = DIFF_APPLY_PROCESSORS[action][stage][self.model_name]
        processor_instance = processor_class()
        logger.info('Processor: %s' % processor_class)

        if action in ACTION_LIST:
            if action == 'add' or action == 'update':
                processor_instance.task_for_selected([target_uuid])
            elif action == 'delete':
                raise NotImplementedError('Precisa implementar ainda!')

            # atualizo registro diff como feito
            diff_model_instance = self.diff_model_class.objects.get(uuid=target_uuid)
            diff_model_instance.done_at = datetime.now()
            diff_model_instance.save()
        else:
            raise ValueError(u'Param action com valor inesperado: %s' % action)


# --------------------------------------------------- #
#                   COLLECTION                        #
# --------------------------------------------------- #


class CollectionDiffer(DifferBase):
    model_name = 'collection'
    ex_model_class = proc_models.ExtractCollection
    tr_model_class = proc_models.TransformCollection
    lo_model_class = proc_models.LoadCollection
    id_model_class = id_models.CollectionIdModel
    diff_model_class = diff_models.CollectionDiffModel


# --------------------------------------------------- #
#                   JOURNALS                          #
# --------------------------------------------------- #


class JournalDiffer(DifferBase):
    model_name = 'journal'
    ex_model_class = proc_models.ExtractJournal
    tr_model_class = proc_models.TransformJournal
    lo_model_class = proc_models.LoadJournal
    id_model_class = id_models.JournalIdModel
    diff_model_class = diff_models.JournalDiffModel


# --------------------------------------------------- #
#                   ISSUES                            #
# --------------------------------------------------- #


class IssueDiffer(DifferBase):
    model_name = 'issue'
    ex_model_class = proc_models.ExtractIssue
    tr_model_class = proc_models.TransformIssue
    lo_model_class = proc_models.LoadIssue
    id_model_class = id_models.IssueIdModel
    diff_model_class = diff_models.IssueDiffModel


# --------------------------------------------------- #
#                   ARTICLE                           #
# --------------------------------------------------- #


class ArticleDiffer(DifferBase):
    model_name = 'article'
    ex_model_class = proc_models.ExtractArticle
    tr_model_class = proc_models.TransformArticle
    lo_model_class = proc_models.LoadArticle
    id_model_class = id_models.ArticleIdModel
    diff_model_class = diff_models.ArticleDiffModel


# --------------------------------------------------- #
#               PRESS RELEASES                        #
# --------------------------------------------------- #


class PressReleaseDiffer(DifferBase):
    model_name = 'press_release'
    ex_model_class = proc_models.ExtractPressRelease
    tr_model_class = proc_models.TransformPressRelease
    lo_model_class = proc_models.LoadPressRelease
    id_model_class = id_models.PressReleaseIdModel
    diff_model_class = diff_models.PressReleaseDiffModel


# --------------------------------------------------- #
#                    NEWS                             #
# --------------------------------------------------- #


class NewsDiffer(DifferBase):
    model_name = 'news'
    ex_model_class = proc_models.ExtractNews
    tr_model_class = proc_models.TransformNews
    lo_model_class = proc_models.LoadNews
    id_model_class = id_models.NewsIdModel
    diff_model_class = diff_models.NewsDiffModel
