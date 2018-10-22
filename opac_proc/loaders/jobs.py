# coding: utf-8
from mongoengine.context_managers import switch_db
from opac_schema.v1 import models as opac_models

from opac_proc.loaders.lo_collections import CollectionLoader
from opac_proc.loaders.lo_journals import JournalLoader
from opac_proc.loaders.lo_issues import IssueLoader
from opac_proc.loaders.lo_articles import ArticleLoader
from opac_proc.loaders.lo_press_releases import PressReleaseLoader
from opac_proc.loaders.lo_news import NewsLoader
from opac_proc.datastore import identifiers_models
from opac_proc.datastore.models import (
    LoadCollection,
    LoadJournal,
    LoadIssue,
    LoadArticle,
    LoadNews,
    LoadPressRelease
)

from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import (
    get_db_connection,
    register_connections,
    get_opac_webapp_db_name
)

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger
from opac_proc.source_sync.utils import chunks

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "load")
else:
    logger = getMongoLogger(__name__, "INFO", "load")

OPAC_WEBAPP_DB_NAME = get_opac_webapp_db_name()

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


def task_delete_selected_collections(selected_uuids):
    """
        Task para apagar Coleções Carregadas.
        @param:
        - selected_uuids: lista de UUIDs dos documentos a serem removidos

        Se a lista `selected_uuids` for maior a SLICE_SIZE
            A lista será fatiada em listas de tamanho: SLICE_SIZE
        Se a lista `selected_uuids` for < a SLICE_SIZE
            Será feito uma delete direto no queryset
    """

    stage = 'load'
    model = 'collection'
    model_class = LoadCollection
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_uuids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_delete_selected_collections, uuid_as_string_list)
    else:
        # removemos o conjunto de documentos do LoadCollection indicados pelos uuids
        documents_to_delete = model_class.objects.filter(uuid__in=selected_uuids)
        documents_to_delete.delete()

        # convertemos os uuid para _id e filtramos esses documentos no OPAC
        register_connections()
        opac_pks = [str(uuid).replace('-', '') for uuid in selected_uuids]
        with switch_db(opac_models.Collection, OPAC_WEBAPP_DB_NAME) as opac_model:
            selected_opac_records = opac_model.objects.filter(pk__in=opac_pks)
            selected_opac_records.delete()


def task_delete_all_collections():
    # removemos todos os documentos do modelo Load Collection (opac-proc)
    get_db_connection()
    all_records = LoadCollection.objects.all()
    all_records.delete()

    register_connections()
    # removemos todos os documentos do modelo Collection (opac)
    with switch_db(opac_models.Collection, OPAC_WEBAPP_DB_NAME) as opac_model:
        all_opac_records = opac_model.objects.all()
        all_opac_records.delete()

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


def task_delete_selected_journals(selected_uuids):
    """
        Task para apagar Journals Carregados.
        @param:
        - selected_uuids: lista de UUIDs dos documentos a serem removidos

        Se a lista `selected_uuids` for maior a SLICE_SIZE
            A lista será fatiada em listas de tamanho: SLICE_SIZE
        Se a lista `selected_uuids` for < a SLICE_SIZE
            Será feito uma delete direto no queryset
    """

    stage = 'load'
    model = 'journal'
    model_class = LoadJournal
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_uuids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_delete_selected_journals, uuid_as_string_list)
    else:
        # removemos o conjunto de documentos do LoadJournal indicados pelos uuids
        documents_to_delete = model_class.objects.filter(uuid__in=selected_uuids)
        documents_to_delete.delete()

        # convertemos os uuid para _id e filtramos esses documentos no OPAC
        register_connections()
        opac_pks = [str(uuid).replace('-', '') for uuid in selected_uuids]
        with switch_db(opac_models.Journal, OPAC_WEBAPP_DB_NAME) as opac_model:
            selected_opac_records = opac_model.objects.filter(pk__in=opac_pks)
            selected_opac_records.delete()


def task_delete_all_journals():
    # removemos todos os documentos do modelo Load Journal (opac-proc)
    get_db_connection()
    all_records = LoadJournal.objects.all()
    all_records.delete()

    # removemos todos os documentos do modelo Journal (opac)
    register_connections()
    with switch_db(opac_models.Journal, OPAC_WEBAPP_DB_NAME) as opac_model:
        all_opac_records = opac_model.objects.all()
        all_opac_records.delete()

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


def task_delete_selected_issues(selected_uuids):
    """
        Task para apagar Issues Carregados.
        @param:
        - selected_uuids: lista de UUIDs dos documentos a serem removidos

        Se a lista `selected_uuids` for maior a SLICE_SIZE
            A lista será fatiada em listas de tamanho: SLICE_SIZE
        Se a lista `selected_uuids` for < a SLICE_SIZE
            Será feito uma delete direto no queryset
    """

    stage = 'load'
    model = 'issue'
    model_class = LoadIssue
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_uuids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_delete_selected_issues, uuid_as_string_list)
    else:
        # removemos o conjunto de documentos do LoadIssues indicados pelos uuids
        documents_to_delete = model_class.objects.filter(uuid__in=selected_uuids)
        documents_to_delete.delete()

        # convertemos os uuid para _id e filtramos esses documentos no OPAC
        register_connections()
        opac_pks = [str(uuid).replace('-', '') for uuid in selected_uuids]
        with switch_db(opac_models.Issue, OPAC_WEBAPP_DB_NAME) as opac_model:
            selected_opac_records = opac_model.objects.filter(pk__in=opac_pks)
            selected_opac_records.delete()


def task_delete_all_issues():
    # removemos todos os documentos do modelo Load Issue (opac-proc)
    get_db_connection()
    all_records = LoadIssue.objects.all()
    all_records.delete()

    # removemos todos os documentos do modelo Issue (opac)
    register_connections()
    with switch_db(opac_models.Issue, OPAC_WEBAPP_DB_NAME) as opac_model:
        all_opac_records = opac_model.objects.all()
        all_opac_records.delete()

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


def task_delete_selected_articles(selected_uuids):
    """
        Task para apagar Articles Carregados.
        @param:
        - selected_uuids: lista de UUIDs dos documentos a serem removidos

        Se a lista `selected_uuids` for maior a SLICE_SIZE
            A lista será fatiada em listas de tamanho: SLICE_SIZE
        Se a lista `selected_uuids` for < a SLICE_SIZE
            Será feito uma delete direto no queryset
    """

    stage = 'load'
    model = 'article'
    model_class = LoadArticle
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_uuids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_delete_selected_articles, uuid_as_string_list)
    else:
        # removemos o conjunto de documentos do LoadArticle indicados pelos uuids
        documents_to_delete = model_class.objects.filter(uuid__in=selected_uuids)
        documents_to_delete.delete()

        # convertemos os uuid para _id e filtramos esses documentos no OPAC
        register_connections()
        opac_pks = [str(uuid).replace('-', '') for uuid in selected_uuids]
        with switch_db(opac_models.Article, OPAC_WEBAPP_DB_NAME) as opac_model:
            selected_opac_records = opac_model.objects.filter(pk__in=opac_pks)
            selected_opac_records.delete()


def task_delete_all_articles():
    # removemos todos os documentos do modelo Load Article (opac-proc)
    get_db_connection()
    all_records = LoadArticle.objects.all()
    all_records.delete()

    # removemos todos os documentos do modelo Article (opac)
    register_connections()
    with switch_db(opac_models.Article, OPAC_WEBAPP_DB_NAME) as opac_model:
        all_opac_records = opac_model.objects.all()
        all_opac_records.delete()


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


def task_delete_selected_press_releases(selected_uuids):
    """
        Task para apagar Press Releases Carregados.
        @param:
        - selected_uuids: lista de UUIDs dos documentos a serem removidos

        Se a lista `selected_uuids` for maior a SLICE_SIZE
            A lista será fatiada em listas de tamanho: SLICE_SIZE
        Se a lista `selected_uuids` for < a SLICE_SIZE
            Será feito uma delete direto no queryset
    """

    stage = 'load'
    model = 'press_release'
    model_class = LoadPressRelease
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_uuids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_delete_selected_press_releases, uuid_as_string_list)
    else:
        # removemos o conjunto de documentos do LoadPressRelease indicados pelos uuids
        documents_to_delete = model_class.objects.filter(uuid__in=selected_uuids)
        documents_to_delete.delete()

        # convertemos os uuid para _id e filtramos esses documentos no OPAC
        register_connections()
        opac_pks = [str(uuid).replace('-', '') for uuid in selected_uuids]
        with switch_db(opac_models.PressRelease, OPAC_WEBAPP_DB_NAME) as opac_model:
            selected_opac_records = opac_model.objects.filter(pk__in=opac_pks)
            selected_opac_records.delete()


def task_delete_all_press_releases():
    # removemos todos os documentos do modelo Load PressRelease (opac-proc)
    get_db_connection()
    all_records = LoadPressRelease.objects.all()
    all_records.delete()

    # removemos todos os documentos do modelo PressRelease (opac)
    register_connections()
    with switch_db(opac_models.PressRelease, OPAC_WEBAPP_DB_NAME) as opac_model:
        all_opac_records = opac_model.objects.all()
        all_opac_records.delete()


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


def task_delete_selected_news(selected_uuids):
    """
        Task para apagar News Carregados.
        @param:
        - selected_uuids: lista de UUIDs dos documentos a serem removidos

        Se a lista `selected_uuids` for maior a SLICE_SIZE
            A lista será fatiada em listas de tamanho: SLICE_SIZE
        Se a lista `selected_uuids` for < a SLICE_SIZE
            Será feito uma delete direto no queryset
    """

    stage = 'load'
    model = 'news'
    model_class = LoadNews
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_uuids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_delete_selected_news, uuid_as_string_list)
    else:
        # removemos o conjunto de documentos do LoadNews indicados pelos uuids
        documents_to_delete = model_class.objects.filter(uuid__in=selected_uuids)
        documents_to_delete.delete()

        # convertemos os uuid para _id e filtramos esses documentos no OPAC
        register_connections()
        opac_pks = [str(uuid).replace('-', '') for uuid in selected_uuids]
        with switch_db(opac_models.News, OPAC_WEBAPP_DB_NAME) as opac_model:
            selected_opac_records = opac_model.objects.filter(pk__in=opac_pks)
            selected_opac_records.delete()


def task_delete_all_news():
    get_db_connection()
    # removemos todos os documentos do modelo Load News (opac-proc)
    all_records = LoadNews.objects.all()
    all_records.delete()

    # removemos todos os documentos do modelo News (opac)
    register_connections()
    with switch_db(opac_models.News, OPAC_WEBAPP_DB_NAME) as opac_model:
        all_opac_records = opac_model.objects.all()
        all_opac_records.delete()
