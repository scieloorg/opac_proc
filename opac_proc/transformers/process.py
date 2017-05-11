# coding: utf-8
from opac_proc.core.process import ProcessTransformBase
from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "transform")
else:
    logger = getMongoLogger(__name__, "INFO", "transform")


class ProcessTransformCollection(ProcessTransformBase):
    model_name = 'collection'
    create_task = 'opac_proc.transformers.jobs.task_collection_create'
    update_task = 'opac_proc.transformers.jobs.task_collection_update'


class ProcessTransformJournal(ProcessTransformBase):
    model_name = 'journal'
    create_task = 'opac_proc.transformers.jobs.task_journal_create'
    update_task = 'opac_proc.transformers.jobs.task_journal_update'


class ProcessTransformIssue(ProcessTransformBase):
    model_name = 'issue'
    create_task = 'opac_proc.transformers.jobs.task_issue_create'
    update_task = 'opac_proc.transformers.jobs.task_issue_update'


class ProcessTransformArticle(ProcessTransformBase):
    model_name = 'article'
    create_task = 'opac_proc.transformers.jobs.task_article_create'
    update_task = 'opac_proc.transformers.jobs.task_article_update'


class ProcessTransformPressRelease(ProcessTransformBase):
    model_name = 'press_release'
    create_task = 'opac_proc.transformers.jobs.task_press_release_create'
    update_task = 'opac_proc.transformers.jobs.task_press_release_update'


class ProcessTransformNews(ProcessTransformBase):
    model_name = 'news'
    create_task = 'opac_proc.transformers.jobs.task_news_create'
    update_task = 'opac_proc.transformers.jobs.task_news_update'
