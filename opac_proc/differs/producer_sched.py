# coding: utf-8

from opac_proc.core.sched import SyncScheduler
from opac_proc.web.config import (
    PRODUCER_BLOGS_CRON_STRING,
    PRODUCER_EXTRACT_CRON_STRING,
    PRODUCER_TRANSFORM_CRON_STRING,
    PRODUCER_LOAD_CRON_STRING,
)


class ProduceAddDifferBase(SyncScheduler):
    stage = 'sync_ids'
    task_func = 'opac_proc.differs.producer_jobs.task_produce_diff_add'


class ProduceUpdateDifferBase(SyncScheduler):
    stage = 'sync_ids'
    task_func = 'opac_proc.differs.producer_jobs.task_produce_diff_update'


class ProduceDeleteDifferBase(SyncScheduler):
    stage = 'sync_ids'
    task_func = 'opac_proc.differs.producer_jobs.task_produce_diff_delete'


# Extract Collection:


class ProduceExtractCollectionAddSched(ProduceAddDifferBase):
    model_name = 'collection'
    cron_string = PRODUCER_EXTRACT_CRON_STRING
    task_args = ['extract', 'collection']


class ProduceExtractCollectionUpdateSched(ProduceUpdateDifferBase):
    model_name = 'collection'
    cron_string = PRODUCER_EXTRACT_CRON_STRING
    task_args = ['extract', 'collection']


class ProduceExtractCollectionDeleteSched(ProduceDeleteDifferBase):
    model_name = 'collection'
    cron_string = PRODUCER_EXTRACT_CRON_STRING
    task_args = ['extract', 'collection']


# Extract Journal:


class ProduceExtractJournalAddSched(ProduceAddDifferBase):
    model_name = 'journal'
    cron_string = PRODUCER_EXTRACT_CRON_STRING
    task_args = ['extract', 'journal']


class ProduceExtractJournalUpdateSched(ProduceUpdateDifferBase):
    model_name = 'journal'
    cron_string = PRODUCER_EXTRACT_CRON_STRING
    task_args = ['extract', 'journal']


class ProduceExtractJournalDeleteSched(ProduceDeleteDifferBase):
    model_name = 'journal'
    cron_string = PRODUCER_EXTRACT_CRON_STRING
    task_args = ['extract', 'journal']


# Extract Issue:


class ProduceExtractIssueAddSched(ProduceAddDifferBase):
    model_name = 'issue'
    cron_string = PRODUCER_EXTRACT_CRON_STRING
    task_args = ['extract', 'issue']


class ProduceExtractIssueUpdateSched(ProduceUpdateDifferBase):
    model_name = 'issue'
    cron_string = PRODUCER_EXTRACT_CRON_STRING
    task_args = ['extract', 'issue']


class ProduceExtractIssueDeleteSched(ProduceDeleteDifferBase):
    model_name = 'issue'
    cron_string = PRODUCER_EXTRACT_CRON_STRING
    task_args = ['extract', 'issue']


# Extract Article:


class ProduceExtractArticleAddSched(ProduceAddDifferBase):
    model_name = 'article'
    cron_string = PRODUCER_EXTRACT_CRON_STRING
    task_args = ['extract', 'article']


class ProduceExtractArticleUpdateSched(ProduceUpdateDifferBase):
    model_name = 'article'
    cron_string = PRODUCER_EXTRACT_CRON_STRING
    task_args = ['extract', 'article']


class ProduceExtractArticleDeleteSched(ProduceDeleteDifferBase):
    model_name = 'article'
    cron_string = PRODUCER_EXTRACT_CRON_STRING
    task_args = ['extract', 'article']


# Extract PressRelease:


class ProduceExtractPressReleaseAddSched(ProduceAddDifferBase):
    model_name = 'press_release'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_args = ['extract', 'press_release']


class ProduceExtractPressReleaseUpdateSched(ProduceUpdateDifferBase):
    model_name = 'press_release'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_args = ['extract', 'press_release']


class ProduceExtractPressReleaseDeleteSched(ProduceDeleteDifferBase):
    model_name = 'press_release'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_args = ['extract', 'press_release']


# Extract News:


class ProduceExtractNewsAddSched(ProduceAddDifferBase):
    model_name = 'news'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_args = ['extract', 'news']


class ProduceExtractNewsUpdateSched(ProduceUpdateDifferBase):
    model_name = 'news'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_args = ['extract', 'news']


class ProduceExtractNewsDeleteSched(ProduceDeleteDifferBase):
    model_name = 'news'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_args = ['extract', 'news']


# Transform Collection:


class ProduceTransformCollectionAddSched(ProduceAddDifferBase):
    model_name = 'collection'
    cron_string = PRODUCER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'collection']


class ProduceTransformCollectionUpdateSched(ProduceUpdateDifferBase):
    model_name = 'collection'
    cron_string = PRODUCER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'collection']


class ProduceTransformCollectionDeleteSched(ProduceDeleteDifferBase):
    model_name = 'collection'
    cron_string = PRODUCER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'collection']


# Transform Journal:


class ProduceTransformJournalAddSched(ProduceAddDifferBase):
    model_name = 'journal'
    cron_string = PRODUCER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'journal']


class ProduceTransformJournalUpdateSched(ProduceUpdateDifferBase):
    model_name = 'journal'
    cron_string = PRODUCER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'journal']


class ProduceTransformJournalDeleteSched(ProduceDeleteDifferBase):
    model_name = 'journal'
    cron_string = PRODUCER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'journal']


# Transform Issue:


class ProduceTransformIssueAddSched(ProduceAddDifferBase):
    model_name = 'issue'
    cron_string = PRODUCER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'issue']


class ProduceTransformIssueUpdateSched(ProduceUpdateDifferBase):
    model_name = 'issue'
    cron_string = PRODUCER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'issue']


class ProduceTransformIssueDeleteSched(ProduceDeleteDifferBase):
    model_name = 'issue'
    cron_string = PRODUCER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'issue']


# Transform Article:


class ProduceTransformArticleAddSched(ProduceAddDifferBase):
    model_name = 'article'
    cron_string = PRODUCER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'article']


class ProduceTransformArticleUpdateSched(ProduceUpdateDifferBase):
    model_name = 'article'
    cron_string = PRODUCER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'article']


class ProduceTransformArticleDeleteSched(ProduceDeleteDifferBase):
    model_name = 'article'
    cron_string = PRODUCER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'article']


# Transform PressRelease:


class ProduceTransformPressReleaseAddSched(ProduceAddDifferBase):
    model_name = 'press_release'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_args = ['transform', 'press_release']


class ProduceTransformPressReleaseUpdateSched(ProduceUpdateDifferBase):
    model_name = 'press_release'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_args = ['transform', 'press_release']


class ProduceTransformPressReleaseDeleteSched(ProduceDeleteDifferBase):
    model_name = 'press_release'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_args = ['transform', 'press_release']


# Transform News:


class ProduceTransformNewsAddSched(ProduceAddDifferBase):
    model_name = 'news'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_args = ['transform', 'news']


class ProduceTransformNewsUpdateSched(ProduceUpdateDifferBase):
    model_name = 'news'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_args = ['transform', 'news']


class ProduceTransformNewsDeleteSched(ProduceDeleteDifferBase):
    model_name = 'news'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_args = ['transform', 'news']


# Load Collection:


class ProduceLoadCollectionAddSched(ProduceAddDifferBase):
    model_name = 'collection'
    cron_string = PRODUCER_LOAD_CRON_STRING
    task_args = ['load', 'collection']


class ProduceLoadCollectionUpdateSched(ProduceUpdateDifferBase):
    model_name = 'collection'
    cron_string = PRODUCER_LOAD_CRON_STRING
    task_args = ['load', 'collection']


class ProduceLoadCollectionDeleteSched(ProduceDeleteDifferBase):
    model_name = 'collection'
    cron_string = PRODUCER_LOAD_CRON_STRING
    task_args = ['load', 'collection']


# Load Journal:


class ProduceLoadJournalAddSched(ProduceAddDifferBase):
    model_name = 'journal'
    cron_string = PRODUCER_LOAD_CRON_STRING
    task_args = ['load', 'journal']


class ProduceLoadJournalUpdateSched(ProduceUpdateDifferBase):
    model_name = 'journal'
    cron_string = PRODUCER_LOAD_CRON_STRING
    task_args = ['load', 'journal']


class ProduceLoadJournalDeleteSched(ProduceDeleteDifferBase):
    model_name = 'journal'
    cron_string = PRODUCER_LOAD_CRON_STRING
    task_args = ['load', 'journal']


# Load Issue:


class ProduceLoadIssueAddSched(ProduceAddDifferBase):
    model_name = 'issue'
    cron_string = PRODUCER_LOAD_CRON_STRING
    task_args = ['load', 'issue']


class ProduceLoadIssueUpdateSched(ProduceUpdateDifferBase):
    model_name = 'issue'
    cron_string = PRODUCER_LOAD_CRON_STRING
    task_args = ['load', 'issue']


class ProduceLoadIssueDeleteSched(ProduceDeleteDifferBase):
    model_name = 'issue'
    cron_string = PRODUCER_LOAD_CRON_STRING
    task_args = ['load', 'issue']


# Load Article:


class ProduceLoadArticleAddSched(ProduceAddDifferBase):
    model_name = 'article'
    cron_string = PRODUCER_LOAD_CRON_STRING
    task_args = ['load', 'article']


class ProduceLoadArticleUpdateSched(ProduceUpdateDifferBase):
    model_name = 'article'
    cron_string = PRODUCER_LOAD_CRON_STRING
    task_args = ['load', 'article']


class ProduceLoadArticleDeleteSched(ProduceDeleteDifferBase):
    model_name = 'article'
    cron_string = PRODUCER_LOAD_CRON_STRING
    task_args = ['load', 'article']


# Load PressRelease:


class ProduceLoadPressReleaseAddSched(ProduceAddDifferBase):
    model_name = 'press_release'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_args = ['load', 'press_release']


class ProduceLoadPressReleaseUpdateSched(ProduceUpdateDifferBase):
    model_name = 'press_release'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_args = ['load', 'press_release']


class ProduceLoadPressReleaseDeleteSched(ProduceDeleteDifferBase):
    model_name = 'press_release'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_args = ['load', 'press_release']


# Load News:


class ProduceLoadNewsAddSched(ProduceAddDifferBase):
    model_name = 'news'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_args = ['load', 'news']


class ProduceLoadNewsUpdateSched(ProduceUpdateDifferBase):
    model_name = 'news'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_args = ['load', 'news']


class ProduceLoadNewsDeleteSched(ProduceDeleteDifferBase):
    model_name = 'news'
    cron_string = PRODUCER_BLOGS_CRON_STRING
    task_args = ['load', 'news']


PRODUCER_SCHEDS = {
    'extract': {
        'collection': {
            'add': ProduceExtractCollectionAddSched,
            'update': ProduceExtractCollectionUpdateSched,
            'delete': ProduceExtractCollectionDeleteSched
        },
        'journal': {
            'add': ProduceExtractJournalAddSched,
            'update': ProduceExtractJournalUpdateSched,
            'delete': ProduceExtractJournalDeleteSched
        },
        'issue': {
            'add': ProduceExtractIssueAddSched,
            'update': ProduceExtractIssueUpdateSched,
            'delete': ProduceExtractIssueDeleteSched,
        },
        'article': {
            'add': ProduceExtractArticleAddSched,
            'update': ProduceExtractArticleUpdateSched,
            'delete': ProduceExtractArticleDeleteSched,
        },
        'press_release': {
            'add': ProduceExtractPressReleaseAddSched,
            'update': ProduceExtractPressReleaseUpdateSched,
            'delete': ProduceExtractPressReleaseDeleteSched
        },
        'news': {
            'add': ProduceExtractNewsAddSched,
            'update': ProduceExtractNewsUpdateSched,
            'delete': ProduceExtractNewsDeleteSched
        }
    },
    'transform': {
        'collection': {
            'add': ProduceTransformCollectionAddSched,
            'update': ProduceTransformCollectionUpdateSched,
            'delete': ProduceTransformCollectionDeleteSched
        },
        'journal': {
            'add': ProduceTransformJournalAddSched,
            'update': ProduceTransformJournalUpdateSched,
            'delete': ProduceTransformJournalDeleteSched
        },
        'issue': {
            'add': ProduceTransformIssueAddSched,
            'update': ProduceTransformIssueUpdateSched,
            'delete': ProduceTransformIssueDeleteSched,
        },
        'article': {
            'add': ProduceTransformArticleAddSched,
            'update': ProduceTransformArticleUpdateSched,
            'delete': ProduceTransformArticleDeleteSched,
        },
        'press_release': {
            'add': ProduceTransformPressReleaseAddSched,
            'update': ProduceTransformPressReleaseUpdateSched,
            'delete': ProduceTransformPressReleaseDeleteSched
        },
        'news': {
            'add': ProduceTransformNewsAddSched,
            'update': ProduceTransformNewsUpdateSched,
            'delete': ProduceTransformNewsDeleteSched
        }
    },
    'load': {
        'collection': {
            'add': ProduceLoadCollectionAddSched,
            'update': ProduceLoadCollectionUpdateSched,
            'delete': ProduceLoadCollectionDeleteSched
        },
        'journal': {
            'add': ProduceLoadJournalAddSched,
            'update': ProduceLoadJournalUpdateSched,
            'delete': ProduceLoadJournalDeleteSched
        },
        'issue': {
            'add': ProduceLoadIssueAddSched,
            'update': ProduceLoadIssueUpdateSched,
            'delete': ProduceLoadIssueDeleteSched,
        },
        'article': {
            'add': ProduceLoadArticleAddSched,
            'update': ProduceLoadArticleUpdateSched,
            'delete': ProduceLoadArticleDeleteSched,
        },
        'press_release': {
            'add': ProduceLoadPressReleaseAddSched,
            'update': ProduceLoadPressReleaseUpdateSched,
            'delete': ProduceLoadPressReleaseDeleteSched
        },
        'news': {
            'add': ProduceLoadNewsAddSched,
            'update': ProduceLoadNewsUpdateSched,
            'delete': ProduceLoadNewsDeleteSched
        }
    }
}
