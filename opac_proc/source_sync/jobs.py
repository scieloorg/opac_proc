# coding: utf-8
from opac_proc.source_sync.utils import chunks
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.datastore.identifiers_models import (
    CollectionIdModel,
    JournalIdModel,
    IssueIdModel,
    ArticleIdModel,
    PressReleaseIdModel,
    NewsIdModel
)

from opac_proc.source_sync.ids_data_retriever import (
    CollectionIdDataRetriever,
    JournalIdDataRetriever,
    IssueIdDataRetriever,
    ArticleIdDataRetriever,
    NewsIdDataRetriever,
    PressReleaseDataRetriever,
)

# --------------------------------------------------- #
#                   COLLECTION                        #
# --------------------------------------------------- #


def task_retrieve_one_collection_identifier(identifier_id):
    """
        Task para processar CollectionIdDataRetriever de
        UM modelo: CollectionIdModel
    """
    retriever_instance = CollectionIdDataRetriever()
    retriever_instance.run_for_one_id(identifier_id)


def task_retrieve_selected_collections_identifiers(selected_ids):
    """
        Task para processar CollectionIdDataRetriever de um LISTA de IDs
        do modelo: CollectionIdModel
    """

    r_queues = RQueues()
    for identifier_id in selected_ids:
        # para o caso da coleção, não precisamos nenhum parâmetro.
        # somente garantimos que rodamos para todos os uuids no banco
        # que deveria ser somente um.
        r_queues.enqueue(
            'sync_ids', 'collection',
            task_retrieve_one_collection_identifier, identifier_id)


def task_retrieve_all_collections_identifiers():
    """
        Task para processar Extração de TODOS os registros do modelo: CollectionIdModel
    """
    r_queues = RQueues()
    retriever_instance = CollectionIdDataRetriever()

    identifiers = retriever_instance.get_data_source_identifiers()
    list_of_all_ids = [identifier for identifier in identifiers]
    list_of_list_of_ids = list(chunks(list_of_all_ids, 1000))

    for list_of_ids in list_of_list_of_ids:
        r_queues.enqueue(
            'sync_ids', 'collection',
            task_retrieve_selected_collections_identifiers, list_of_ids)


def task_delete_selected_collections_identifiers(selected_ids):
    """
        Task para apagar identificadores de Coleção.
        @param:
        - selected_ids: lista de pk dos documentos a serem removidos

        Se a lista `selected_ids` for maior a SLICE_SIZE
            A lista será fatiada em listas de tamanho: SLICE_SIZE
        Se a lista `selected_ids` for < a SLICE_SIZE
            Será feito uma delete direto no queryset
    """

    model_class = CollectionIdModel
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_ids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_ids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(
                'sync_ids', 'collection',
                task_delete_selected_collections_identifiers, uuid_as_string_list)
    else:
        documents_to_delete = model_class.objects.filter(pk__in=selected_ids)
        documents_to_delete.delete()


def task_delete_all_collections_identifiers():
    get_db_connection()
    all_records = CollectionIdModel.objects.all()
    all_records.delete()


# --------------------------------------------------- #
#                   JOURNALS                          #
# --------------------------------------------------- #


def task_retrieve_one_journal_identifier(identifier_id):
    """
        Task para processar JournalIdDataRetriever de
        UM modelo: JournalIdModel
    """
    retriever_instance = JournalIdDataRetriever()
    retriever_instance.run_for_one_id(identifier_id)


def task_retrieve_selected_journals_identifiers(selected_ids):
    """
        Task para processar JournalIdDataRetriever de um LISTA de IDs
        do modelo: JournalIdModel
    """

    r_queues = RQueues()
    for identifier_id in selected_ids:
        r_queues.enqueue(
            'sync_ids', 'journal',
            task_retrieve_one_journal_identifier, identifier_id)


def task_retrieve_all_journals_identifiers():
    """
        Task para processar Extração de TODOS os registros do modelo: JournalIdModel
    """
    r_queues = RQueues()
    retriever_instance = JournalIdDataRetriever()

    identifiers = retriever_instance.get_data_source_identifiers()
    list_of_all_ids = [identifier for identifier in identifiers]
    list_of_list_of_ids = list(chunks(list_of_all_ids, 1000))

    for list_of_ids in list_of_list_of_ids:
        r_queues.enqueue(
            'sync_ids', 'journal',
            task_retrieve_selected_journals_identifiers, list_of_ids)


def task_delete_selected_journals_identifiers(selected_ids):
    """
        Task para apagar identificadores de Journal.
        @param:
        - selected_ids: lista de pk dos documentos a serem removidos

        Se a lista `selected_ids` for maior a SLICE_SIZE
            A lista será fatiada em listas de tamanho: SLICE_SIZE
        Se a lista `selected_ids` for < a SLICE_SIZE
            Será feito uma delete direto no queryset
    """

    model_class = JournalIdModel
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_ids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_ids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue('sync_ids', 'journal', task_delete_selected_journals_identifiers, uuid_as_string_list)
    else:
        documents_to_delete = model_class.objects.filter(pk__in=selected_ids)
        documents_to_delete.delete()


def task_delete_all_journals_identifiers():
    get_db_connection()
    all_records = JournalIdModel.objects.all()
    all_records.delete()


# --------------------------------------------------- #
#                   ISSUES                            #
# --------------------------------------------------- #
def task_retrieve_one_issue_identifier(identifier_id):
    """
        Task para processar IssueIdDataRetriever de
        UM modelo: IssueIdModel
    """
    retriever_instance = IssueIdDataRetriever()
    retriever_instance.run_for_one_id(identifier_id)


def task_retrieve_selected_issues_identifiers(selected_ids):
    """
        Task para processar IssueIdDataRetriever de um LISTA de IDs
        do modelo: IssueIdModel
    """

    r_queues = RQueues()
    for identifier_id in selected_ids:
        r_queues.enqueue(
            'sync_ids', 'issue',
            task_retrieve_one_issue_identifier, identifier_id)


def task_retrieve_all_issues_identifiers():
    """
        Task para processar Extração de TODOS os registros do modelo: IssueIdModel
    """
    r_queues = RQueues()
    retriever_instance = IssueIdDataRetriever()

    identifiers = retriever_instance.get_data_source_identifiers()
    list_of_all_ids = [identifier for identifier in identifiers]
    list_of_list_of_ids = list(chunks(list_of_all_ids, 1000))

    for list_of_ids in list_of_list_of_ids:
        r_queues.enqueue(
            'sync_ids', 'issue',
            task_retrieve_selected_issues_identifiers, list_of_ids)


def task_delete_selected_issues_identifiers(selected_ids):
    """
        Task para apagar identificadores de Issue.
        @param:
        - selected_ids: lista de pk dos documentos a serem removidos

        Se a lista `selected_ids` for maior a SLICE_SIZE
            A lista será fatiada em listas de tamanho: SLICE_SIZE
        Se a lista `selected_ids` for < a SLICE_SIZE
            Será feito uma delete direto no queryset
    """

    model_class = IssueIdModel
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_ids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_ids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(
                'sync_ids', 'issue',
                task_delete_selected_issues_identifiers, uuid_as_string_list)
    else:
        documents_to_delete = model_class.objects.filter(pk__in=selected_ids)
        documents_to_delete.delete()


def task_delete_all_issues_identifiers():
    get_db_connection()
    all_records = IssueIdModel.objects.all()
    all_records.delete()


# --------------------------------------------------- #
#                   ARTICLE                           #
# --------------------------------------------------- #


def task_retrieve_one_article_identifier(identifier_id):
    """
        Task para processar ArticleIdDataRetriever de
        UM modelo: ArticleIdModel
    """
    retriever_instance = ArticleIdDataRetriever()
    retriever_instance.run_for_one_id(identifier_id)


def task_retrieve_selected_articles_identifiers(selected_ids):
    """
        Task para processar ArticleIdDataRetriever de um LISTA de IDs
        do modelo: IssueIdModel
    """

    r_queues = RQueues()
    for identifier_id in selected_ids:
        r_queues.enqueue(
            'sync_ids', 'article',
            task_retrieve_one_article_identifier, identifier_id)


def task_retrieve_all_articles_identifiers():
    """
        Task para processar Extração de TODOS os registros do modelo: ArticleIdModel
    """
    r_queues = RQueues()
    retriever_instance = ArticleIdDataRetriever()

    identifiers = retriever_instance.get_data_source_identifiers()
    list_of_all_ids = [identifier for identifier in identifiers]
    list_of_list_of_ids = list(chunks(list_of_all_ids, 1000))

    for list_of_ids in list_of_list_of_ids:
        r_queues.enqueue(
            'sync_ids', 'article',
            task_retrieve_selected_articles_identifiers, list_of_ids)


def task_delete_selected_articles_identifiers(selected_ids):
    """
        Task para apagar identificadores de Article.
        @param:
        - selected_ids: lista de pk dos documentos a serem removidos

        Se a lista `selected_ids` for maior a SLICE_SIZE
            A lista será fatiada em listas de tamanho: SLICE_SIZE
        Se a lista `selected_ids` for < a SLICE_SIZE
            Será feito uma delete direto no queryset
    """

    model_class = ArticleIdModel
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_ids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_ids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(
                'sync_ids', 'article',
                task_delete_selected_articles_identifiers, uuid_as_string_list)
    else:
        documents_to_delete = model_class.objects.filter(pk__in=selected_ids)
        documents_to_delete.delete()


def task_delete_all_articles_identifiers():
    get_db_connection()
    all_records = ArticleIdModel.objects.all()
    all_records.delete()


# --------------------------------------------------- #
#               PRESS RELEASES                        #
# --------------------------------------------------- #

def task_retrieve_one_press_release_identifier(identifier_id):
    """
        Task para processar PressReleaseIdDataRetriever de
        UM modelo: ArticleIdModel
    """
    retriever_instance = PressReleaseDataRetriever()
    retriever_instance.run_for_one_id(identifier_id)


def task_retrieve_selected_press_releases_identifiers(selected_ids):
    """
        Task para processar PressReleaseDataRetriever de um LISTA de IDs
        do modelo: PressRelaseIdModel
    """

    r_queues = RQueues()
    for identifier_id in selected_ids:
        r_queues.enqueue(
            'sync_ids', 'press_release',
            task_retrieve_one_press_release_identifier, identifier_id)


def task_retrieve_all_press_releases_identifiers():
    """
        Task para processar Extração de TODOS os registros do modelo: PressRelaseIdModel
    """
    r_queues = RQueues()
    retriever_instance = PressReleaseDataRetriever()

    identifiers = retriever_instance.get_data_source_identifiers()
    list_of_all_ids = [identifier for identifier in identifiers]
    list_of_list_of_ids = list(chunks(list_of_all_ids, 1000))

    for list_of_ids in list_of_list_of_ids:
        r_queues.enqueue(
            'sync_ids', 'press_release',
            task_retrieve_selected_press_releases_identifiers, list_of_ids)


def task_delete_selected_press_releases_identifiers(selected_ids):
    """
        Task para apagar identificadores de Press Release.
        @param:
        - selected_ids: lista de pk dos documentos a serem removidos

        Se a lista `selected_ids` for maior a SLICE_SIZE
            A lista será fatiada em listas de tamanho: SLICE_SIZE
        Se a lista `selected_ids` for < a SLICE_SIZE
            Será feito uma delete direto no queryset
    """

    model_class = PressReleaseIdModel
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_ids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_ids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(
                'sync_ids', 'press_release',
                task_delete_selected_press_releases_identifiers, uuid_as_string_list)
    else:
        documents_to_delete = model_class.objects.filter(pk__in=selected_ids)
        documents_to_delete.delete()


def task_delete_all_press_releases_identifiers():
    get_db_connection()
    all_records = PressReleaseIdModel.objects.all()
    all_records.delete()


# --------------------------------------------------- #
#                    NEWS                             #
# --------------------------------------------------- #


def task_retrieve_one_news_identifier(identifier_id):
    """
        Task para processar NewsIdDataRetriever de
        UM modelo: ArticleIdModel
    """
    retriever_instance = NewsIdDataRetriever()
    retriever_instance.run_for_one_id(identifier_id)


def task_retrieve_selected_news_identifiers(selected_ids):
    """
        Task para processar NewsIdDataRetriever de um LISTA de IDs
        do modelo: NewsIdModel
    """

    r_queues = RQueues()
    for identifier_id in selected_ids:
        r_queues.enqueue(
            'sync_ids', 'news',
            task_retrieve_one_news_identifier, identifier_id)


def task_retrieve_all_news_identifiers():
    """
        Task para processar Extração de TODOS os registros do modelo: NewsIdModel
    """
    r_queues = RQueues()
    retriever_instance = NewsIdDataRetriever()

    identifiers = retriever_instance.get_data_source_identifiers()
    list_of_all_ids = [identifier for identifier in identifiers]
    list_of_list_of_ids = list(chunks(list_of_all_ids, 1000))

    for list_of_ids in list_of_list_of_ids:
        r_queues.enqueue(
            'sync_ids', 'news',
            task_retrieve_selected_news_identifiers, list_of_ids)


def task_delete_selected_news_identifiers(selected_ids):
    """
        Task para apagar identificadores de News.
        @param:
        - selected_ids: lista de pk dos documentos a serem removidos

        Se a lista `selected_ids` for maior a SLICE_SIZE
            A lista será fatiada em listas de tamanho: SLICE_SIZE
        Se a lista `selected_ids` for < a SLICE_SIZE
            Será feito uma delete direto no queryset
    """

    model_class = NewsIdModel
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_ids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_ids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(
                'sync_ids', 'news',
                task_delete_selected_news_identifiers, uuid_as_string_list)
    else:
        documents_to_delete = model_class.objects.filter(pk__in=selected_ids)
        documents_to_delete.delete()


def task_delete_all_news_identifiers():
    get_db_connection()
    all_records = NewsIdModel.objects.all()
    all_records.delete()
