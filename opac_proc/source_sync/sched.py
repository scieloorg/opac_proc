# coding: utf-8

from opac_proc.core.sched import SyncScheduler
from opac_proc.web.config import (
    RETRIEVE_IDENTIFIERS_CRON_STRING,
    PRODUCER_BLOGS_CRON_STRING
)


class BaseIdSyncScheduler(SyncScheduler):
    stage = 'sync_ids'
    cron_string = RETRIEVE_IDENTIFIERS_CRON_STRING


class CollectionIdSyncScheduler(BaseIdSyncScheduler):
    model_name = 'collection'
    task_func = 'opac_proc.source_sync.jobs.task_retrieve_all_collections_identifiers'


class JournalIdSyncScheduler(BaseIdSyncScheduler):
    model_name = 'journal'
    task_func = 'opac_proc.source_sync.jobs.task_retrieve_all_journals_identifiers'


class IssueIdSyncScheduler(BaseIdSyncScheduler):
    model_name = 'issue'
    task_func = 'opac_proc.source_sync.jobs.task_retrieve_all_issues_identifiers'


class ArticleIdSyncScheduler(BaseIdSyncScheduler):
    model_name = 'article'
    task_func = 'opac_proc.source_sync.jobs.task_retrieve_all_articles_identifiers'


class PressReleaseIdSyncScheduler(SyncScheduler):
    stage = 'sync_ids'
    model_name = 'press_release'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_func = 'opac_proc.source_sync.jobs.task_retrieve_all_press_releases_identifiers'


class NewsIdSyncScheduler(SyncScheduler):
    stage = 'sync_ids'
    model_name = 'news'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_func = 'opac_proc.source_sync.jobs.task_retrieve_all_news_identifiers'


SCHED_ID_BY_MODEL_NAME = {
    'collection': CollectionIdSyncScheduler,
    'journal': JournalIdSyncScheduler,
    'issue': IssueIdSyncScheduler,
    'article': ArticleIdSyncScheduler,
    'press_release': PressReleaseIdSyncScheduler,
    'news': NewsIdSyncScheduler,
}
