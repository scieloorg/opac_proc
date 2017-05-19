# coding: utf-8
from opac_proc.core.process import ProcessExtractBase
from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "extract")
else:
    logger = getMongoLogger(__name__, "INFO", "extract")


class ProcessExtractCollection(ProcessExtractBase):
    model_name = 'collection'
    create_task = 'opac_proc.extractors.jobs.task_collection_create'
    update_task = 'opac_proc.extractors.jobs.task_collection_update'


class ProcessExtractJournal(ProcessExtractBase):
    model_name = 'journal'
    create_task = 'opac_proc.extractors.jobs.task_journal_create'
    update_task = 'opac_proc.extractors.jobs.task_journal_update'


class ProcessExtractIssue(ProcessExtractBase):
    model_name = 'issue'
    create_task = 'opac_proc.extractors.jobs.task_issue_create'
    update_task = 'opac_proc.extractors.jobs.task_issue_update'


class ProcessExtractArticle(ProcessExtractBase):
    model_name = 'article'
    create_task = 'opac_proc.extractors.jobs.task_article_create'
    update_task = 'opac_proc.extractors.jobs.task_article_update'


class ProcessExtractPressRelease(ProcessExtractBase):
    model_name = 'press_release'
    create_task = 'opac_proc.extractors.jobs.task_press_release_create'
    update_task = 'opac_proc.extractors.jobs.task_press_release_update'


class ProcessExtractNews(ProcessExtractBase):
    model_name = 'news'
    create_task = 'opac_proc.extractors.jobs.task_news_create'
    update_task = 'opac_proc.extractors.jobs.task_news_update'
