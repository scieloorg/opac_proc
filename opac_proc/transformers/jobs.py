# coding: utf-8
from opac_proc.transformers.tr_collections import CollectionTransformer
from opac_proc.transformers.tr_journals import JournalTransformer
from opac_proc.transformers.tr_issues import IssueTransformer
from opac_proc.transformers.tr_articles import ArticleTransformer
from opac_proc.transformers.tr_press_releases import PressReleaseTransformer
from opac_proc.transformers.tr_news import NewsTransformer

from opac_proc.datastore import identifiers_models
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import get_db_connection

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger
from opac_proc.source_sync.utils import chunks

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "transform")
else:
    logger = getMongoLogger(__name__, "INFO", "transform")

# --------------------------------------------------- #
#                   COLLECTION                        #
# --------------------------------------------------- #


def task_transform_one_collection():
    """
        Task para processar Tranformação de UM modelo: Collection
    """
    acronym = config.OPAC_PROC_COLLECTION
    transformer = CollectionTransformer(extract_model_key=acronym)
    transformer.transform()
    transformer.save()


def task_transform_selected_collections(selected_uuids):
    """
        Task para processar Transformação de um LISTA de UUIDs do modelo: Collection
    """

    r_queues = RQueues()
    for uuid in selected_uuids:
        # para o caso da coleção, não precisamos nenhum parâmetro.
        # somente garantimos que rodamos para todos os uuids no banco
        # que deveria ser somente um.
        r_queues.enqueue('transform', 'collection', task_transform_one_collection)


def task_transform_all_collections():
    """
        Task para processar Transformação de TODOS os registros do modelo: Collection
    """
    stage = 'transform'
    model = 'collection'
    source_ids_model_class = identifiers_models.CollectionIdModel
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    list_of_all_uuids = source_ids_model_class.objects.all().values_list('uuid')
    if len(list_of_all_uuids) <= SLICE_SIZE:
        uuid_as_string_list = [str(uuid) for uuid in list_of_all_uuids]
        r_queues.enqueue(stage, model, task_transform_selected_collections, uuid_as_string_list)
    else:
        list_of_list_of_uuids = list(chunks(list_of_all_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_transform_selected_collections, uuid_as_string_list)


# --------------------------------------------------- #
#                   JOURNALS                          #
# --------------------------------------------------- #


def task_transform_one_journal(issn):
    """
        Task para processar Tranformação de UM modelo: Journal
    """
    transformer = JournalTransformer(extract_model_key=issn)
    transformer.transform()
    transformer.save()


def task_transform_selected_journals(selected_uuids):
    """
        Task para processar Transformação de um LISTA de UUIDs do modelo: Journal
    """
    get_db_connection()
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.JournalIdModel
    issns_iter = source_ids_model_class.objects.filter(uuid__in=selected_uuids).values_list('journal_issn')
    for issn in issns_iter:
        r_queues.enqueue('transform', 'journal', task_transform_one_journal, issn)


def task_transform_all_journals():
    """
        Task para processar Transformação de TODOS os registros do modelo: Journal
    """
    get_db_connection()
    stage = 'transform'
    model = 'journal'
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.JournalIdModel
    SLICE_SIZE = 1000

    list_of_all_uuids = source_ids_model_class.objects.all().values_list('uuid')
    if len(list_of_all_uuids) <= SLICE_SIZE:
        uuid_as_string_list = [str(uuid) for uuid in list_of_all_uuids]
        r_queues.enqueue(stage, model, task_transform_selected_journals, uuid_as_string_list)
    else:
        list_of_list_of_uuids = list(chunks(list_of_all_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_transform_selected_journals, uuid_as_string_list)


# --------------------------------------------------- #
#                   ISSUES                            #
# --------------------------------------------------- #


def task_transform_one_issue(issue_pid):
    """
        Task para processar Tranformação de UM modelo: Issue
    """
    transformer = IssueTransformer(extract_model_key=issue_pid)
    transformer.transform()
    transformer.save()


def task_transform_selected_issues(selected_uuids):
    """
        Task para processar Transformação de um LISTA de UUIDs do modelo: Issue
    """
    get_db_connection()
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.IssueIdModel

    pids_iter = source_ids_model_class.objects.filter(uuid__in=selected_uuids).values_list('issue_pid')
    for issue_pid in pids_iter:
        r_queues.enqueue('transform', 'issue', task_transform_one_issue, issue_pid)


def task_transform_all_issues():
    """
        Task para processar Transformação de TODOS os registros do modelo: Issue
    """
    get_db_connection()
    stage = 'transform'
    model = 'issue'
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.IssueIdModel
    SLICE_SIZE = 1000

    list_of_all_uuids = source_ids_model_class.objects.all().values_list('uuid')
    if len(list_of_all_uuids) <= SLICE_SIZE:
        uuid_as_string_list = [str(uuid) for uuid in list_of_all_uuids]
        r_queues.enqueue(stage, model, task_transform_selected_issues, uuid_as_string_list)
    else:
        list_of_list_of_uuids = list(chunks(list_of_all_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_transform_selected_issues, uuid_as_string_list)


# --------------------------------------------------- #
#                   ARTICLE                           #
# --------------------------------------------------- #


def task_transform_one_article(article_pid):
    """
        Task para processar Tranformação de UM modelo: Article
    """
    transformer = ArticleTransformer(extract_model_key=article_pid)
    transformer.transform()
    transformer.save()


def task_transform_selected_articles(selected_uuids):
    """
        Task para processar Transformação de um LISTA de UUIDs do modelo: Article
    """
    get_db_connection()
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.ArticleIdModel

    pids_iter = source_ids_model_class.objects.filter(uuid__in=selected_uuids).values_list('article_pid')
    for article_pid in pids_iter:
        r_queues.enqueue('transform', 'article', task_transform_one_article, article_pid)


def task_transform_all_articles():
    """
        Task para processar Transformação de TODOS os registros do modelo: Article
    """
    get_db_connection()
    stage = 'transform'
    model = 'article'
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.ArticleIdModel
    SLICE_SIZE = 1000

    list_of_all_uuids = source_ids_model_class.objects.all().values_list('uuid')
    if len(list_of_all_uuids) <= SLICE_SIZE:
        uuid_as_string_list = [str(uuid) for uuid in list_of_all_uuids]
        r_queues.enqueue(stage, model, task_transform_selected_articles, uuid_as_string_list)
    else:
        list_of_list_of_uuids = list(chunks(list_of_all_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_transform_selected_articles, uuid_as_string_list)


# --------------------------------------------------- #
#               PRESS RELEASES                        #
# --------------------------------------------------- #


def task_transform_one_press_release(press_release_uuid):
    """
        Task para processar Transformação de UM modelo: Press Release
    """
    transformer = PressReleaseTransformer(extract_model_key=press_release_uuid)
    transformer.transform()
    transformer.save()


def task_transform_selected_press_releases(selected_uuids):
    """
        Task para processar Transformação de um LISTA de UUIDs do modelo: Press Release
    """
    r_queues = RQueues()

    for uuid in selected_uuids:
        r_queues.enqueue('transform', 'press_release',
                         task_transform_one_press_release,
                         uuid)


def task_transform_all_press_releases():
    """
        Task para processar Transformação de TODOS os registros do modelo: Press Release
    """
    get_db_connection()
    stage = 'transform'
    model = 'press_release'
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.PressReleaseIdModel
    SLICE_SIZE = 1000

    list_of_all_uuids = source_ids_model_class.objects.all().values_list('uuid')
    if len(list_of_all_uuids) <= SLICE_SIZE:
        uuid_as_string_list = [str(uuid) for uuid in list_of_all_uuids]
        r_queues.enqueue(stage, model, task_transform_selected_press_releases, uuid_as_string_list)
    else:
        list_of_list_of_uuids = list(chunks(list_of_all_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_transform_selected_press_releases, uuid_as_string_list)


# --------------------------------------------------- #
#                    NEWS                             #
# --------------------------------------------------- #


def task_transform_one_news(news_uuid):
    """
        Task para processar Tranformação de UM modelo: News
    """
    transformer = NewsTransformer(extract_model_key=news_uuid)
    transformer.transform()
    transformer.save()


def task_transform_selected_news(selected_uuids):
    """
        Task para processar Transformação de um LISTA de UUIDs do modelo: News
    """
    r_queues = RQueues()

    for uuid in selected_uuids:
        r_queues.enqueue('transform', 'news',
                         task_transform_one_news,
                         uuid)


def task_transform_all_news():
    """
        Task para processar Transformação de TODOS os registros do modelo: News
    """
    get_db_connection()
    stage = 'transform'
    model = 'news'
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.NewsIdModel
    SLICE_SIZE = 1000

    list_of_all_uuids = source_ids_model_class.objects.all().values_list('uuid')
    if len(list_of_all_uuids) <= SLICE_SIZE:
        uuid_as_string_list = [str(uuid) for uuid in list_of_all_uuids]
        r_queues.enqueue(stage, model, task_transform_selected_news, uuid_as_string_list)
    else:
        list_of_list_of_uuids = list(chunks(list_of_all_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_transform_selected_news, uuid_as_string_list)
