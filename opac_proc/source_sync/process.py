# coding: utf-8
from opac_proc.core.process import ProcessIdentifiersBase


class ProcessIdentifiersCollection(ProcessIdentifiersBase):
    model_name = 'collection'
    task_for_selected = 'opac_proc.source_sync.jobs.task_retrieve_selected_collections_identifiers'
    task_for_all = 'opac_proc.source_sync.jobs.task_retrieve_all_collections_identifiers'
    task_delete_selected = 'opac_proc.source_sync.jobs.task_delete_selected_collections_identifiers'
    task_delete_all = 'opac_proc.source_sync.jobs.task_delete_all_collections_identifiers'


class ProcessIdentifiersJournal(ProcessIdentifiersBase):
    model_name = 'journal'
    task_for_selected = 'opac_proc.source_sync.jobs.task_retrieve_selected_journals_identifiers'
    task_for_all = 'opac_proc.source_sync.jobs.task_retrieve_all_journals_identifiers'
    task_delete_selected = 'opac_proc.source_sync.jobs.task_delete_selected_journals_identifiers'
    task_delete_all = 'opac_proc.source_sync.jobs.task_delete_all_journals_identifiers'


class ProcessIdentifiersIssue(ProcessIdentifiersBase):
    model_name = 'issue'
    task_for_selected = 'opac_proc.source_sync.jobs.task_retrieve_selected_issues_identifiers'
    task_for_all = 'opac_proc.source_sync.jobs.task_retrieve_all_issues_identifiers'
    task_delete_selected = 'opac_proc.source_sync.jobs.task_delete_selected_issues_identifiers'
    task_delete_all = 'opac_proc.source_sync.jobs.task_delete_all_issues_identifiers'


class ProcessIdentifiersArticle(ProcessIdentifiersBase):
    model_name = 'article'
    task_for_selected = 'opac_proc.source_sync.jobs.task_retrieve_selected_articles_identifiers'
    task_for_all = 'opac_proc.source_sync.jobs.task_retrieve_all_articles_identifiers'
    task_delete_selected = 'opac_proc.source_sync.jobs.task_delete_selected_articles_identifiers'
    task_delete_all = 'opac_proc.source_sync.jobs.task_delete_all_articles_identifiers'


class ProcessIdentifiersPressRelease(ProcessIdentifiersBase):
    model_name = 'press_release'
    task_for_selected = 'opac_proc.source_sync.jobs.task_retrieve_selected_press_releases_identifiers'
    task_for_all = 'opac_proc.source_sync.jobs.task_retrieve_all_press_releases_identifiers'
    task_delete_selected = 'opac_proc.source_sync.jobs.task_delete_selected_press_releases_identifiers'
    task_delete_all = 'opac_proc.source_sync.jobs.task_delete_all_press_releases_identifiers'


class ProcessIdentifiersNews(ProcessIdentifiersBase):
    model_name = 'news'
    task_for_selected = 'opac_proc.source_sync.jobs.task_retrieve_selected_news_identifiers'
    task_for_all = 'opac_proc.source_sync.jobs.task_retrieve_all_news_identifiers'
    task_delete_selected = 'opac_proc.source_sync.jobs.task_delete_selected_news_identifiers'
    task_delete_all = 'opac_proc.source_sync.jobs.task_delete_all_news_identifiers'
