# coding: utf-8
from opac_proc.core.process import ProcessTransformBase


class ProcessTransformCollection(ProcessTransformBase):
    model_name = 'collection'
    task_for_selected = 'opac_proc.transformers.jobs.task_transform_selected_collections'
    task_for_all = 'opac_proc.transformers.jobs.task_transform_all_collections'
    task_delete_selected = 'opac_proc.transformers.jobs.task_delete_selected_collections'
    task_delete_all = 'opac_proc.transformers.jobs.task_delete_all_collections'


class ProcessTransformJournal(ProcessTransformBase):
    model_name = 'journal'
    task_for_selected = 'opac_proc.transformers.jobs.task_transform_selected_journals'
    task_for_all = 'opac_proc.transformers.jobs.task_transform_all_journals'
    task_delete_selected = 'opac_proc.transformers.jobs.task_delete_selected_journals'
    task_delete_all = 'opac_proc.transformers.jobs.task_delete_all_journals'


class ProcessTransformIssue(ProcessTransformBase):
    model_name = 'issue'
    task_for_selected = 'opac_proc.transformers.jobs.task_transform_selected_issues'
    task_for_all = 'opac_proc.transformers.jobs.task_transform_all_issues'
    task_delete_selected = 'opac_proc.transformers.jobs.task_delete_selected_issues'
    task_delete_all = 'opac_proc.transformers.jobs.task_delete_all_issues'


class ProcessTransformArticle(ProcessTransformBase):
    model_name = 'article'
    task_for_selected = 'opac_proc.transformers.jobs.task_transform_selected_articles'
    task_for_all = 'opac_proc.transformers.jobs.task_transform_all_articles'
    task_delete_selected = 'opac_proc.transformers.jobs.task_delete_selected_articles'
    task_delete_all = 'opac_proc.transformers.jobs.task_delete_all_articles'


class ProcessTransformPressRelease(ProcessTransformBase):
    model_name = 'press_release'
    task_for_selected = 'opac_proc.transformers.jobs.task_transform_selected_press_releases'
    task_for_all = 'opac_proc.transformers.jobs.task_transform_all_press_releases'
    task_delete_selected = 'opac_proc.transformers.jobs.task_delete_selected_press_releases'
    task_delete_all = 'opac_proc.transformers.jobs.task_delete_all_press_releases'


class ProcessTransformNews(ProcessTransformBase):
    model_name = 'news'
    task_for_selected = 'opac_proc.transformers.jobs.task_transform_selected_news'
    task_for_all = 'opac_proc.transformers.jobs.task_transform_all_news'
    task_delete_selected = 'opac_proc.transformers.jobs.task_delete_selected_news'
    task_delete_all = 'opac_proc.transformers.jobs.task_delete_all_news'
