# coding: utf-8

from opac_proc.core.sched import SyncScheduler


class CollectionIdSyncScheduler(SyncScheduler):
    stage = 'sync_ids'
    model_name = 'collection'
    cron_string = '0,30 5-23 * * 3,6'
    task_func = 'opac_proc.source_sync.jobs.task_retrieve_all_collections_identifiers'


class JournalIdSyncScheduler(SyncScheduler):
    stage = 'sync_ids'
    model_name = 'journal'
    cron_string = '0,30 5-23 * * 3,6'
    task_func = 'opac_proc.source_sync.jobs.task_retrieve_all_journals_identifiers'


class IssueIdSyncScheduler(SyncScheduler):
    stage = 'sync_ids'
    model_name = 'issue'
    cron_string = '0,30 5-23 * * 3,6'
    task_func = 'opac_proc.source_sync.jobs.task_retrieve_all_issues_identifiers'


class ArticleIdSyncScheduler(SyncScheduler):
    stage = 'sync_ids'
    model_name = 'article'
    cron_string = '0,30 5-23 * * 3,6'
    task_func = 'opac_proc.source_sync.jobs.task_retrieve_all_articles_identifiers'


class PressReleaseIdSyncScheduler(SyncScheduler):
    stage = 'sync_ids'
    model_name = 'press_release'
    cron_string = '0,30 * * * *'
    task_func = 'opac_proc.source_sync.jobs.task_retrieve_all_press_releases_identifiers'


class NewsIdSyncScheduler(SyncScheduler):
    stage = 'sync_ids'
    model_name = 'news'
    cron_string = '0,30 * * * *'
    task_func = 'opac_proc.source_sync.jobs.task_retrieve_all_news_identifiers'


SCHED_ID_BY_MODEL_NAME = {
    'collection': CollectionIdSyncScheduler,
    'journal': JournalIdSyncScheduler,
    'issue': IssueIdSyncScheduler,
    'article': ArticleIdSyncScheduler,
    'press_release': PressReleaseIdSyncScheduler,
    'news': NewsIdSyncScheduler,
}
