# coding: utf-8
from opac_proc.datastore import diff_models
from etl_differ import (
    CollectionDiffer,
    JournalDiffer,
    IssueDiffer,
    ArticleDiffer,
    PressReleaseDiffer,
    NewsDiffer,
)

DIFF_MODEL_CLASS_BY_NAME = {
    'collection': diff_models.CollectionDiffModel,
    'journal': diff_models.JournalDiffModel,
    'issue': diff_models.IssueDiffModel,
    'article': diff_models.ArticleDiffModel,
    'news': diff_models.NewsDiffModel,
    'press_release': diff_models.PressReleaseDiffModel,
}

ETL_DIFFERS_BY_MODEL = {
    'collection': CollectionDiffer,
    'journal': JournalDiffer,
    'issue': IssueDiffer,
    'article': ArticleDiffer,
    'news': NewsDiffer,
    'press_release': PressReleaseDiffer,
}

ETL_MODEL_NAME_LIST = [
    'collection',
    'journal',
    'issue',
    'article',
    'news',
    'press_release'
]

ETL_STAGE_LIST = [
    'extract',
    'transform',
    'load'
]

ACTION_LIST = [
    'add',
    'update',
    'delete'
]
