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
    task_for_selected = 'opac_proc.transformers.jobs.task_transform_selected_collections'
    task_for_all = 'opac_proc.transformers.jobs.task_transform_all_collections'


class ProcessTransformJournal(ProcessTransformBase):
    model_name = 'journal'
    task_for_selected = 'opac_proc.transformers.jobs.task_transform_selected_journals'
    task_for_all = 'opac_proc.transformers.jobs.task_transform_all_journals'


class ProcessTransformIssue(ProcessTransformBase):
    model_name = 'issue'
    task_for_selected = 'opac_proc.transformers.jobs.task_transform_selected_issues'
    task_for_all = 'opac_proc.transformers.jobs.task_transform_all_issues'


class ProcessTransformArticle(ProcessTransformBase):
    model_name = 'article'
    task_for_selected = 'opac_proc.transformers.jobs.task_transform_selected_articles'
    task_for_all = 'opac_proc.transformers.jobs.task_transform_all_articles'


class ProcessTransformPressRelease(ProcessTransformBase):
    model_name = 'press_release'
    task_for_selected = 'opac_proc.transformers.jobs.task_transform_selected_press_releases'
    task_for_all = 'opac_proc.transformers.jobs.task_transform_all_press_releases'


class ProcessTransformNews(ProcessTransformBase):
    model_name = 'news'
    task_for_selected = 'opac_proc.transformers.jobs.task_transform_selected_news'
    task_for_all = 'opac_proc.transformers.jobs.task_transform_all_news'
