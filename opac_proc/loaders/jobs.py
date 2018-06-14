# coding: utf-8

from opac_proc.loaders.lo_collections import CollectionLoader
from opac_proc.loaders.lo_journals import JournalLoader
from opac_proc.loaders.lo_issues import IssueLoader
from opac_proc.loaders.lo_articles import ArticleLoader
from opac_proc.loaders.lo_press_releases import PressReleaseLoader
from opac_proc.loaders.lo_news import NewsLoader
from opac_proc.datastore import identifiers_models

from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger
from opac_proc.source_sync.utils import chunks

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "load")
else:
    logger = getMongoLogger(__name__, "INFO", "load")


# --------------------------------------------------- #
#                   COLLECTION                        #
# --------------------------------------------------- #


def task_load_one_collection(uuid):
    """
        Task para processar Carga de UM modelo: Collection
    """
    c_loader = CollectionLoader(uuid)
    c_loader.prepare()
    c_loader.load()


def task_load_selected_collections(selected_uuids):
    """
        Task para processar Carga de um LISTA de UUIDs do modelo: Collection
    """

    r_queues = RQueues()
    for uuid in selected_uuids:
        r_queues.enqueue('load', 'collection', task_load_one_collection, uuid)


def task_load_all_collections():
    """
        Task para processar Carga de TODOS os registros do modelo: Collection
    """
    stage = 'load'
    model = 'collection'
    source_ids_model_class = identifiers_models.CollectionIdModel
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    list_of_all_uuids = source_ids_model_class.objects.all().values_list('uuid')
    if len(list_of_all_uuids) <= SLICE_SIZE:
        uuid_as_string_list = [str(uuid) for uuid in list_of_all_uuids]
        r_queues.enqueue(stage, model, task_load_selected_collections, uuid_as_string_list)
    else:
        list_of_list_of_uuids = list(chunks(list_of_all_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_load_selected_collections, uuid_as_string_list)


# --------------------------------------------------- #
#                   JOURNALS                          #
# --------------------------------------------------- #


def task_load_one_journal(uuid):
    """
        Task para processar Carga de UM modelo: Journal
    """
    j_loader = JournalLoader(uuid)
    j_loader.prepare()
    j_loader.load()


def task_load_selected_journals(selected_uuids):
    """
        Task para processar Carga de um LISTA de UUIDs do modelo: Journal
    """
    r_queues = RQueues()
    for uuid in selected_uuids:
        r_queues.enqueue('load', 'journal', task_load_one_journal, uuid)


def task_load_all_journals():
    """
        Task para processar Carga de TODOS os registros do modelo: Journal
    """
    get_db_connection()
    stage = 'load'
    model = 'journal'
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.JournalIdModel
    SLICE_SIZE = 1000

    list_of_all_uuids = source_ids_model_class.objects.all().values_list('uuid')
    if len(list_of_all_uuids) <= SLICE_SIZE:
        uuid_as_string_list = [str(uuid) for uuid in list_of_all_uuids]
        r_queues.enqueue(stage, model, task_load_selected_journals, uuid_as_string_list)
    else:
        list_of_list_of_uuids = list(chunks(list_of_all_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_load_selected_journals, uuid_as_string_list)


# --------------------------------------------------- #
#                   ISSUES                            #
# --------------------------------------------------- #


def task_load_one_issue(uuid):
    """
        Task para processar Carga de UM modelo: Issue
    """
    i_loader = IssueLoader(uuid)
    i_loader.prepare()
    i_loader.load()


def task_load_selected_issues(selected_uuids):
    """
        Task para processar Carga de um LISTA de UUIDs do modelo: Issue
    """
    r_queues = RQueues()
    for uuid in selected_uuids:
        r_queues.enqueue('load', 'issue', task_load_one_issue, uuid)


def task_load_all_issues():
    """
        Task para processar Carga de TODOS os registros do modelo: Issue
    """
    get_db_connection()
    stage = 'load'
    model = 'issue'
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.IssueIdModel
    SLICE_SIZE = 1000

    list_of_all_uuids = source_ids_model_class.objects.all().values_list('uuid')
    if len(list_of_all_uuids) <= SLICE_SIZE:
        uuid_as_string_list = [str(uuid) for uuid in list_of_all_uuids]
        r_queues.enqueue(stage, model, task_load_selected_issues, uuid_as_string_list)
    else:
        list_of_list_of_uuids = list(chunks(list_of_all_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_load_selected_issues, uuid_as_string_list)


# --------------------------------------------------- #
#                   ARTICLE                           #
# --------------------------------------------------- #


def task_load_one_article(uuid):
    """
        Task para processar Carga de UM modelo: Article
    """
    a_loader = ArticleLoader(uuid)
    a_loader.prepare()
    a_loader.load()


def task_load_selected_articles(selected_uuids):
    """
        Task para processar Carga de um LISTA de UUIDs do modelo: Article
    """
    r_queues = RQueues()
    for uuid in selected_uuids:
        r_queues.enqueue('load', 'article', task_load_one_article, uuid)


def task_load_all_articles():
    """
        Task para processar Carga de TODOS os registros do modelo: Article
    """
    get_db_connection()
    stage = 'load'
    model = 'article'
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.ArticleIdModel
    SLICE_SIZE = 1000

    list_of_all_uuids = source_ids_model_class.objects.all().values_list('uuid')
    if len(list_of_all_uuids) <= SLICE_SIZE:
        uuid_as_string_list = [str(uuid) for uuid in list_of_all_uuids]
        r_queues.enqueue(stage, model, task_load_selected_articles, uuid_as_string_list)
    else:
        list_of_list_of_uuids = list(chunks(list_of_all_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_load_selected_articles, uuid_as_string_list)


# --------------------------------------------------- #
#               PRESS RELEASES                        #
# --------------------------------------------------- #


def task_load_one_press_release(uuid):
    """
        Task para processar Carga de UM modelo: Press Release
    """
    pr_loader = PressReleaseLoader(uuid)
    pr_loader.prepare()
    pr_loader.load()


def task_load_selected_press_releases(selected_uuids):
    """
        Task para processar Carga de um LISTA de UUIDs do modelo: Press Release
    """
    r_queues = RQueues()
    for uuid in selected_uuids:
        r_queues.enqueue('load', 'press_release', task_load_one_press_release, uuid)


def task_load_all_press_releases():
    """
        Task para processar Carga de TODOS os registros do modelo: Press Release
    """
    get_db_connection()
    stage = 'load'
    model = 'press_release'
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.PressReleaseIdModel
    SLICE_SIZE = 1000

    list_of_all_uuids = source_ids_model_class.objects.all().values_list('uuid')
    if len(list_of_all_uuids) <= SLICE_SIZE:
        uuid_as_string_list = [str(uuid) for uuid in list_of_all_uuids]
        r_queues.enqueue(stage, model, task_load_selected_press_releases, uuid_as_string_list)
    else:
        list_of_list_of_uuids = list(chunks(list_of_all_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_load_selected_press_releases, uuid_as_string_list)


# --------------------------------------------------- #
#                    NEWS                             #
# --------------------------------------------------- #


def task_load_one_news(uuid):
    """
        Task para processar Carga de UM modelo: News
    """
    news_loader = NewsLoader(uuid)
    news_loader.prepare()
    news_loader.load()


def task_load_selected_news(selected_uuids):
    """
        Task para processar Carga de um LISTA de UUIDs do modelo: News
    """
    r_queues = RQueues()
    for uuid in selected_uuids:
        r_queues.enqueue('load', 'news', task_load_one_news, uuid)


def task_load_all_news():
    """
        Task para processar Carga de TODOS os registros do modelo: News
    """
    get_db_connection()
    stage = 'load'
    model = 'news'
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.NewsIdModel
    SLICE_SIZE = 1000

    list_of_all_uuids = source_ids_model_class.objects.all().values_list('uuid')
    if len(list_of_all_uuids) <= SLICE_SIZE:
        uuid_as_string_list = [str(uuid) for uuid in list_of_all_uuids]
        r_queues.enqueue(stage, model, task_load_selected_news, uuid_as_string_list)
    else:
        list_of_list_of_uuids = list(chunks(list_of_all_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_load_selected_news, uuid_as_string_list)
