# coding: utf-8
from opac_proc.extractors.source_clients.amapi_wrapper import custom_amapi_client

from opac_proc.extractors.ex_collections import CollectionExtractor
from opac_proc.extractors.ex_journals import JournalExtractor
from opac_proc.extractors.ex_issues import IssueExtractor
from opac_proc.extractors.ex_articles import ArticleExtractor
from opac_proc.extractors.ex_press_releases import PressReleaseExtractor
from opac_proc.extractors.ex_news import NewsExtractor

from opac_proc.datastore import identifiers_models
from opac_proc.datastore.models import (
    ExtractCollection,
    ExtractJournal,
    ExtractIssue,
    ExtractArticle,
    ExtractNews,
    ExtractPressRelease
)
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import get_db_connection

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger
from opac_proc.source_sync.utils import chunks

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "extract")
else:
    logger = getMongoLogger(__name__, "INFO", "extract")


# --------------------------------------------------- #
#                   COLLECTION                        #
# --------------------------------------------------- #


def task_extract_one_collection():
    """
        Task para processar Extração de UM modelo: Collection
    """
    extractor = CollectionExtractor()
    extractor.extract()
    extractor.save()


def task_extract_selected_collections(selected_uuids):
    """
        Task para processar Extração de um LISTA de UUIDs do modelo: Collection
    """

    r_queues = RQueues()
    for uuid in selected_uuids:
        # para o caso da coleção, não precisamos nenhum parâmetro.
        # somente garantimos que rodamos para todos os uuids no banco
        # que deveria ser somente um.
        r_queues.enqueue('extract', 'collection', task_extract_one_collection)


def task_extract_all_collections():
    """
        Task para processar Extração de TODOS os registros do modelo: Collection
    """
    stage = 'extract'
    model = 'collection'
    source_ids_model_class = identifiers_models.CollectionIdModel
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    list_of_all_uuids = source_ids_model_class.objects.all().values_list('uuid')
    if len(list_of_all_uuids) <= SLICE_SIZE:
        uuid_as_string_list = [str(uuid) for uuid in list_of_all_uuids]
        r_queues.enqueue(stage, model, task_extract_selected_collections, uuid_as_string_list)
    else:
        list_of_list_of_uuids = list(chunks(list_of_all_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_extract_selected_collections, uuid_as_string_list)


def task_delete_selected_collections(selected_ids):
    """
        Task para apagar Coleções Extaidas.
        @param:
        - selected_ids: lista de pk dos documentos a serem removidos

        Se a lista `selected_ids` for maior a SLICE_SIZE
            A lista será fatiada em listas de tamanho: SLICE_SIZE
        Se a lista `selected_ids` for < a SLICE_SIZE
            Será feito uma delete direto no queryset
    """

    stage = 'extract'
    model = 'collection'
    model_class = ExtractCollection
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_ids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_ids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_delete_selected_collections, uuid_as_string_list)
    else:
        documents_to_delete = model_class.objects.filter(pk__in=selected_ids)
        documents_to_delete.delete()


def task_delete_all_collections():
    get_db_connection()
    all_records = ExtractCollection.objects.all()
    all_records.delete()


# --------------------------------------------------- #
#                   JOURNALS                          #
# --------------------------------------------------- #


def task_extract_one_journal(issn):
    """
        Task para processar Extração de UM modelo: Journal
    """
    extractor = JournalExtractor(issn)
    extractor.extract()
    extractor.save()


def task_extract_selected_journals(selected_uuids):
    """
        Task para processar Extração de um LISTA de UUIDs do modelo: Journal
    """
    get_db_connection()
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.JournalIdModel
    issns_iter = source_ids_model_class.objects.filter(uuid__in=selected_uuids).values_list('journal_issn')
    for issn in issns_iter:
        r_queues.enqueue('extract', 'journal', task_extract_one_journal, issn)


def task_extract_all_journals():
    """
        Task para processar Extração de TODOS os registros do modelo: Journal
    """
    get_db_connection()
    stage = 'extract'
    model = 'journal'
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.JournalIdModel
    SLICE_SIZE = 1000

    list_of_all_uuids = source_ids_model_class.objects.all().values_list('uuid')
    if len(list_of_all_uuids) <= SLICE_SIZE:
        uuid_as_string_list = [str(uuid) for uuid in list_of_all_uuids]
        r_queues.enqueue(stage, model, task_extract_selected_journals, uuid_as_string_list)
    else:
        list_of_list_of_uuids = list(chunks(list_of_all_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_extract_selected_journals, uuid_as_string_list)


def task_delete_selected_journals(selected_ids):
    """
        Task para apagar Journals Extaidaos.
        @param:
        - selected_ids: lista de pk dos documentos a serem removidos

        Se a lista `selected_ids` for maior a SLICE_SIZE
            A lista será fatiada em listas de tamanho: SLICE_SIZE
        Se a lista `selected_ids` for < a SLICE_SIZE
            Será feito uma delete direto no queryset
    """

    stage = 'extract'
    model = 'journal'
    model_class = ExtractJournal
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_ids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_ids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_delete_selected_journals, uuid_as_string_list)
    else:
        documents_to_delete = model_class.objects.filter(pk__in=selected_ids)
        documents_to_delete.delete()


def task_delete_all_journals():
    get_db_connection()
    all_records = ExtractJournal.objects.all()
    all_records.delete()


# --------------------------------------------------- #
#                   ISSUES                            #
# --------------------------------------------------- #

def task_extract_one_issue(issue_pid):
    """
        Task para processar Extração de UM modelo: Issue
    """
    extractor = IssueExtractor(issue_pid)
    extractor.extract()
    extractor.save()


def task_extract_selected_issues(selected_uuids):
    """
        Task para processar Extração de um LISTA de UUIDs do modelo: Issue
    """
    get_db_connection()
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.IssueIdModel
    pids_iter = source_ids_model_class.objects.filter(uuid__in=selected_uuids).values_list('issue_pid')
    for issue_pid in pids_iter:
        r_queues.enqueue('extract', 'issue', task_extract_one_issue, issue_pid)


def task_extract_all_issues():
    """
        Task para processar Extração de TODOS os registros do modelo: Issue
    """
    get_db_connection()
    stage = 'extract'
    model = 'issue'
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.IssueIdModel
    SLICE_SIZE = 1000

    list_of_all_uuids = source_ids_model_class.objects.all().values_list('uuid')
    if len(list_of_all_uuids) <= SLICE_SIZE:
        uuid_as_string_list = [str(uuid) for uuid in list_of_all_uuids]
        r_queues.enqueue(stage, model, task_extract_selected_issues, uuid_as_string_list)
    else:
        list_of_list_of_uuids = list(chunks(list_of_all_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_extract_selected_issues, uuid_as_string_list)


def task_delete_selected_issues(selected_ids):
    """
        Task para apagar Issues Extaidaos.
        @param:
        - selected_ids: lista de pk dos documentos a serem removidos

        Se a lista `selected_ids` for maior a SLICE_SIZE
            A lista será fatiada em listas de tamanho: SLICE_SIZE
        Se a lista `selected_ids` for < a SLICE_SIZE
            Será feito uma delete direto no queryset
    """

    stage = 'extract'
    model = 'issue'
    model_class = ExtractIssue
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_ids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_ids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_delete_selected_issues, uuid_as_string_list)
    else:
        documents_to_delete = model_class.objects.filter(pk__in=selected_ids)
        documents_to_delete.delete()


def task_delete_all_issues():
    get_db_connection()
    all_records = ExtractIssue.objects.all()
    all_records.delete()


# --------------------------------------------------- #
#                   ARTICLE                           #
# --------------------------------------------------- #


def task_extract_one_article(article_pid):
    """
        Task para processar Extração de UM modelo: Article
    """
    extractor = ArticleExtractor(article_pid)
    extractor.extract()
    extractor.save()


def task_extract_selected_articles(selected_uuids):
    """
        Task para processar Extração de um LISTA de UUIDs do modelo: Issue
    """
    get_db_connection()
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.ArticleIdModel

    pids_iter = source_ids_model_class.objects.filter(uuid__in=selected_uuids).values_list('article_pid')
    for article_pid in pids_iter:
        r_queues.enqueue('extract', 'article', task_extract_one_article, article_pid)


def task_extract_all_articles(uuids=None):
    """
        Task para processar Extração de TODOS os registros do modelo: Article
    """
    get_db_connection()
    stage = 'extract'
    model = 'article'
    r_queues = RQueues()
    source_ids_model_class = identifiers_models.ArticleIdModel
    SLICE_SIZE = 1000

    list_of_all_uuids = source_ids_model_class.objects.all().values_list('uuid')
    if len(list_of_all_uuids) <= SLICE_SIZE:
        uuid_as_string_list = [str(uuid) for uuid in list_of_all_uuids]
        r_queues.enqueue(stage, model, task_extract_selected_articles, uuid_as_string_list)
    else:
        list_of_list_of_uuids = list(chunks(list_of_all_uuids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_extract_selected_articles, uuid_as_string_list)


def task_delete_selected_articles(selected_ids):
    """
        Task para apagar Articles Extaidaos.
        @param:
        - selected_ids: lista de pk dos documentos a serem removidos

        Se a lista `selected_ids` for maior a SLICE_SIZE
            A lista será fatiada em listas de tamanho: SLICE_SIZE
        Se a lista `selected_ids` for < a SLICE_SIZE
            Será feito uma delete direto no queryset
    """

    stage = 'extract'
    model = 'article'
    model_class = ExtractArticle
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_ids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_ids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_delete_selected_articles, uuid_as_string_list)
    else:
        documents_to_delete = model_class.objects.filter(pk__in=selected_ids)
        documents_to_delete.delete()


def task_delete_all_articles():
    get_db_connection()
    all_records = ExtractArticle.objects.all()
    all_records.delete()


# --------------------------------------------------- #
#               PRESS RELEASES                        #
# --------------------------------------------------- #


def task_extract_one_press_release(journal_acronym, url, lang):
    """
        Task para processar Extração de UM modelo: Press Release
    """
    extractor = PressReleaseExtractor(journal_acronym, url, lang)
    pr_entries = extractor.get_feed_entries()
    for pr_entry in pr_entries:
        extractor.extract(pr_entry)
        extractor.save()


def task_extract_selected_press_releases(selected_uuids):
    """
        Task para processar Extração de um LISTA de UUIDs do modelo: Press Release
    """
    get_db_connection()
    r_queues = RQueues()

    extracted_press_releases_selected = ExtractPressRelease.objects.filter(uuid__in=selected_uuids)
    for ex_pr in extracted_press_releases_selected:
        r_queues.enqueue('extract', 'press_release',
                         task_extract_one_press_release,
                         ex_pr.journal_acronym,
                         ex_pr.feed_url_used, ex_pr.feed_lang)


def task_extract_all_press_releases():
    """
        Task para processar Extração de TODOS os registros do modelo: Press Release
    """

    def get_all_journals_acronyms():

        client = custom_amapi_client.ArticleMeta(
            config.ARTICLE_META_THRIFT_DOMAIN,
            config.ARTICLE_META_THRIFT_PORT,
            config.ARTICLE_META_THRIFT_TIMEOUT)
        acronyms = [j.acronym for j in client.get_xylose_journals(collection=config.OPAC_PROC_COLLECTION)]
        return acronyms

    r_queues = RQueues()
    journal_acronyms = get_all_journals_acronyms()
    for j_acronym in journal_acronyms:
        for lang, feed in config.RSS_PRESS_RELEASES_FEEDS_BY_CATEGORY.items():
            feed_url_by_lang = feed['url'].format(lang, j_acronym)
            r_queues.enqueue('extract', 'press_release',
                             task_extract_one_press_release,
                             j_acronym, feed_url_by_lang, lang)


def task_delete_selected_press_releases(selected_ids):
    """
        Task para apagar Press Releases Extaidaos.
        @param:
        - selected_ids: lista de pk dos documentos a serem removidos

        Se a lista `selected_ids` for maior a SLICE_SIZE
            A lista será fatiada em listas de tamanho: SLICE_SIZE
        Se a lista `selected_ids` for < a SLICE_SIZE
            Será feito uma delete direto no queryset
    """

    stage = 'extract'
    model = 'press_release'
    model_class = ExtractPressRelease
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_ids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_ids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_delete_selected_press_releases, uuid_as_string_list)
    else:
        documents_to_delete = model_class.objects.filter(pk__in=selected_ids)
        documents_to_delete.delete()


def task_delete_all_press_releases():
    get_db_connection()
    all_records = ExtractPressRelease.objects.all()
    all_records.delete()


# --------------------------------------------------- #
#                    NEWS                             #
# --------------------------------------------------- #


def task_extract_one_news(url, lang):
    """
        Task para processar Extração de UM modelo: News
    """
    extractor = NewsExtractor(url, lang)
    news_entries = extractor.get_feed_entries()
    for news_entry in news_entries:
        extractor.extract(news_entry)
        extractor.save()


def task_extract_selected_news(selected_uuids):
    """
        Task para processar Extração de um LISTA de UUIDs do modelo: News
    """
    get_db_connection()
    r_queues = RQueues()

    extracted_news_selected = ExtractNews.objects.filter(uuid__in=selected_uuids)
    for ex_news in extracted_news_selected:
        r_queues.enqueue('extract', 'news',
                         task_extract_one_news,
                         ex_news.feed_url_used, ex_news.feed_lang)


def task_extract_all_news():
    """
        Task para processar Extração de TODOS os registros do modelo: News
    """

    stage = 'extract'
    model = 'news'
    r_queues = RQueues()

    for lang, feed in config.RSS_NEWS_FEEDS.items():
        url = feed['url'].format(lang)
        r_queues.enqueue(
            stage, model,
            task_extract_one_news,
            url, lang)


def task_delete_selected_news(selected_ids):
    """
        Task para apagar News Extaidaos.
        @param:
        - selected_ids: lista de pk dos documentos a serem removidos

        Se a lista `selected_ids` for maior a SLICE_SIZE
            A lista será fatiada em listas de tamanho: SLICE_SIZE
        Se a lista `selected_ids` for < a SLICE_SIZE
            Será feito uma delete direto no queryset
    """

    stage = 'extract'
    model = 'press_release'
    model_class = ExtractPressRelease
    get_db_connection()
    r_queues = RQueues()
    SLICE_SIZE = 1000

    if len(selected_ids) > SLICE_SIZE:
        list_of_list_of_uuids = list(chunks(selected_ids, SLICE_SIZE))
        for list_of_uuids in list_of_list_of_uuids:
            uuid_as_string_list = [str(uuid) for uuid in list_of_uuids]
            r_queues.enqueue(stage, model, task_delete_selected_news, uuid_as_string_list)
    else:
        documents_to_delete = model_class.objects.filter(pk__in=selected_ids)
        documents_to_delete.delete()


def task_delete_all_news():
    get_db_connection()
    all_records = ExtractPressRelease.objects.all()
    all_records.delete()
