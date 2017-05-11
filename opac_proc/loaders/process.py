# coding: utf-8
from opac_proc.core.process import ProcessLoadBase
from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "load")
else:
    logger = getMongoLogger(__name__, "INFO", "load")


class ProcessLoadCollection(ProcessLoadBase):
    model_name = 'collection'
    create_task = 'opac_proc.loaders.jobs.task_collection_create'
    update_task = 'opac_proc.loaders.jobs.task_collection_update'


class ProcessLoadJournal(ProcessLoadBase):
    model_name = 'journal'
    create_task = 'opac_proc.loaders.jobs.task_journal_create'
    update_task = 'opac_proc.loaders.jobs.task_journal_update'


class ProcessLoadIssue(ProcessLoadBase):
    model_name = 'issue'
    create_task = 'opac_proc.loaders.jobs.task_issue_create'
    update_task = 'opac_proc.loaders.jobs.task_issue_update'


class ProcessLoadArticle(ProcessLoadBase):
    model_name = 'article'
    create_task = 'opac_proc.loaders.jobs.task_article_create'
    update_task = 'opac_proc.loaders.jobs.task_article_update'


class ProcessLoadPressRelease(ProcessLoadBase):
    model_name = 'press_release'
    create_task = 'opac_proc.loaders.jobs.task_press_release_create'
    update_task = 'opac_proc.loaders.jobs.task_press_release_update'


class ProcessLoadNews(ProcessLoadBase):
    model_name = 'news'
    create_task = 'opac_proc.loaders.jobs.task_news_create'
    update_task = 'opac_proc.loaders.jobs.task_news_update'
