# coding: utf-8

from opac_proc.core.sched import SyncScheduler
from opac_proc.web.config import (
    CONSUMER_BLOGS_CRON_STRING,
    CONSUMER_EXTRACT_CRON_STRING,
    CONSUMER_TRANSFORM_CRON_STRING,
    CONSUMER_LOAD_CRON_STRING,
)


class ConsumeAddDifferBase(SyncScheduler):
    stage = 'sync_ids'
    task_func = 'opac_proc.differs.consumer_jobs.task_consume_diff_add'


class ConsumeUpdateDifferBase(SyncScheduler):
    stage = 'sync_ids'
    task_func = 'opac_proc.differs.consumer_jobs.task_consume_diff_update'


class ConsumeDeleteDifferBase(SyncScheduler):
    stage = 'sync_ids'
    task_func = 'opac_proc.differs.consumer_jobs.task_consume_diff_delete'


# Extract Collection:


class ConsumeExtractCollectionAddSched(ConsumeAddDifferBase):
    model_name = 'collection'
    cron_string = CONSUMER_EXTRACT_CRON_STRING
    task_args = ['extract', 'collection']


class ConsumeExtractCollectionUpdateSched(ConsumeUpdateDifferBase):
    model_name = 'collection'
    cron_string = CONSUMER_EXTRACT_CRON_STRING
    task_args = ['extract', 'collection']


class ConsumeExtractCollectionDeleteSched(ConsumeDeleteDifferBase):
    model_name = 'collection'
    cron_string = CONSUMER_EXTRACT_CRON_STRING
    task_args = ['extract', 'collection']


# Extract Journal:


class ConsumeExtractJournalAddSched(ConsumeAddDifferBase):
    model_name = 'journal'
    cron_string = CONSUMER_EXTRACT_CRON_STRING
    task_args = ['extract', 'journal']


class ConsumeExtractJournalUpdateSched(ConsumeUpdateDifferBase):
    model_name = 'journal'
    cron_string = CONSUMER_EXTRACT_CRON_STRING
    task_args = ['extract', 'journal']


class ConsumeExtractJournalDeleteSched(ConsumeDeleteDifferBase):
    model_name = 'journal'
    cron_string = CONSUMER_EXTRACT_CRON_STRING
    task_args = ['extract', 'journal']


# Extract Issue:


class ConsumeExtractIssueAddSched(ConsumeAddDifferBase):
    model_name = 'issue'
    cron_string = CONSUMER_EXTRACT_CRON_STRING
    task_args = ['extract', 'issue']


class ConsumeExtractIssueUpdateSched(ConsumeUpdateDifferBase):
    model_name = 'issue'
    cron_string = CONSUMER_EXTRACT_CRON_STRING
    task_args = ['extract', 'issue']


class ConsumeExtractIssueDeleteSched(ConsumeDeleteDifferBase):
    model_name = 'issue'
    cron_string = CONSUMER_EXTRACT_CRON_STRING
    task_args = ['extract', 'issue']


# Extract Article:


class ConsumeExtractArticleAddSched(ConsumeAddDifferBase):
    model_name = 'article'
    cron_string = CONSUMER_EXTRACT_CRON_STRING
    task_args = ['extract', 'article']


class ConsumeExtractArticleUpdateSched(ConsumeUpdateDifferBase):
    model_name = 'article'
    cron_string = CONSUMER_EXTRACT_CRON_STRING
    task_args = ['extract', 'article']


class ConsumeExtractArticleDeleteSched(ConsumeDeleteDifferBase):
    model_name = 'article'
    cron_string = CONSUMER_EXTRACT_CRON_STRING
    task_args = ['extract', 'article']


# Extract PressRelease:


class ConsumeExtractPressReleaseAddSched(ConsumeAddDifferBase):
    model_name = 'press_release'
    cron_string = CONSUMER_BLOGS_CRON_STRING
    task_args = ['extract', 'press_release']


class ConsumeExtractPressReleaseUpdateSched(ConsumeUpdateDifferBase):
    model_name = 'press_release'
    cron_string = CONSUMER_BLOGS_CRON_STRING
    task_args = ['extract', 'press_release']


class ConsumeExtractPressReleaseDeleteSched(ConsumeDeleteDifferBase):
    model_name = 'press_release'
    cron_string = CONSUMER_BLOGS_CRON_STRING
    task_args = ['extract', 'press_release']


# Extract News:


class ConsumeExtractNewsAddSched(ConsumeAddDifferBase):
    model_name = 'news'
    cron_string = CONSUMER_BLOGS_CRON_STRING
    task_args = ['extract', 'news']


class ConsumeExtractNewsUpdateSched(ConsumeUpdateDifferBase):
    model_name = 'news'
    cron_string = CONSUMER_BLOGS_CRON_STRING
    task_args = ['extract', 'news']


class ConsumeExtractNewsDeleteSched(ConsumeDeleteDifferBase):
    model_name = 'news'
    cron_string = CONSUMER_BLOGS_CRON_STRING
    task_args = ['extract', 'news']


# Transform Collection:


class ConsumeTransformCollectionAddSched(ConsumeAddDifferBase):
    model_name = 'collection'
    cron_string = CONSUMER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'collection']


class ConsumeTransformCollectionUpdateSched(ConsumeUpdateDifferBase):
    model_name = 'collection'
    cron_string = CONSUMER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'collection']


class ConsumeTransformCollectionDeleteSched(ConsumeDeleteDifferBase):
    model_name = 'collection'
    cron_string = CONSUMER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'collection']


# Transform Journal:


class ConsumeTransformJournalAddSched(ConsumeAddDifferBase):
    model_name = 'journal'
    cron_string = CONSUMER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'journal']


class ConsumeTransformJournalUpdateSched(ConsumeUpdateDifferBase):
    model_name = 'journal'
    cron_string = CONSUMER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'journal']


class ConsumeTransformJournalDeleteSched(ConsumeDeleteDifferBase):
    model_name = 'journal'
    cron_string = CONSUMER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'journal']


# Transform Issue:


class ConsumeTransformIssueAddSched(ConsumeAddDifferBase):
    model_name = 'issue'
    cron_string = CONSUMER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'issue']


class ConsumeTransformIssueUpdateSched(ConsumeUpdateDifferBase):
    model_name = 'issue'
    cron_string = CONSUMER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'issue']


class ConsumeTransformIssueDeleteSched(ConsumeDeleteDifferBase):
    model_name = 'issue'
    cron_string = CONSUMER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'issue']


# Transform Article:


class ConsumeTransformArticleAddSched(ConsumeAddDifferBase):
    model_name = 'article'
    cron_string = CONSUMER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'article']


class ConsumeTransformArticleUpdateSched(ConsumeUpdateDifferBase):
    model_name = 'article'
    cron_string = CONSUMER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'article']


class ConsumeTransformArticleDeleteSched(ConsumeDeleteDifferBase):
    model_name = 'article'
    cron_string = CONSUMER_TRANSFORM_CRON_STRING
    task_args = ['transform', 'article']


# Transform PressRelease:


class ConsumeTransformPressReleaseAddSched(ConsumeAddDifferBase):
    model_name = 'press_release'
    cron_string = CONSUMER_BLOGS_CRON_STRING
    task_args = ['transform', 'press_release']


class ConsumeTransformPressReleaseUpdateSched(ConsumeUpdateDifferBase):
    model_name = 'press_release'
    cron_string = CONSUMER_BLOGS_CRON_STRING
    task_args = ['transform', 'press_release']


class ConsumeTransformPressReleaseDeleteSched(ConsumeDeleteDifferBase):
    model_name = 'press_release'
    cron_string = CONSUMER_BLOGS_CRON_STRING
    task_args = ['transform', 'press_release']


# Transform News:


class ConsumeTransformNewsAddSched(ConsumeAddDifferBase):
    model_name = 'news'
    cron_string = CONSUMER_BLOGS_CRON_STRING
    task_args = ['transform', 'news']


class ConsumeTransformNewsUpdateSched(ConsumeUpdateDifferBase):
    model_name = 'news'
    cron_string = CONSUMER_BLOGS_CRON_STRING
    task_args = ['transform', 'news']


class ConsumeTransformNewsDeleteSched(ConsumeDeleteDifferBase):
    model_name = 'news'
    cron_string = CONSUMER_BLOGS_CRON_STRING
    task_args = ['transform', 'news']


# Load Collection:


class ConsumeLoadCollectionAddSched(ConsumeAddDifferBase):
    model_name = 'collection'
    cron_string = CONSUMER_LOAD_CRON_STRING
    task_args = ['load', 'collection']


class ConsumeLoadCollectionUpdateSched(ConsumeUpdateDifferBase):
    model_name = 'collection'
    cron_string = CONSUMER_LOAD_CRON_STRING
    task_args = ['load', 'collection']


class ConsumeLoadCollectionDeleteSched(ConsumeDeleteDifferBase):
    model_name = 'collection'
    cron_string = CONSUMER_LOAD_CRON_STRING
    task_args = ['load', 'collection']


# Load Journal:


class ConsumeLoadJournalAddSched(ConsumeAddDifferBase):
    model_name = 'journal'
    cron_string = CONSUMER_LOAD_CRON_STRING
    task_args = ['load', 'journal']


class ConsumeLoadJournalUpdateSched(ConsumeUpdateDifferBase):
    model_name = 'journal'
    cron_string = CONSUMER_LOAD_CRON_STRING
    task_args = ['load', 'journal']


class ConsumeLoadJournalDeleteSched(ConsumeDeleteDifferBase):
    model_name = 'journal'
    cron_string = CONSUMER_LOAD_CRON_STRING
    task_args = ['load', 'journal']


# Load Issue:


class ConsumeLoadIssueAddSched(ConsumeAddDifferBase):
    model_name = 'issue'
    cron_string = CONSUMER_LOAD_CRON_STRING
    task_args = ['load', 'issue']


class ConsumeLoadIssueUpdateSched(ConsumeUpdateDifferBase):
    model_name = 'issue'
    cron_string = CONSUMER_LOAD_CRON_STRING
    task_args = ['load', 'issue']


class ConsumeLoadIssueDeleteSched(ConsumeDeleteDifferBase):
    model_name = 'issue'
    cron_string = CONSUMER_LOAD_CRON_STRING
    task_args = ['load', 'issue']


# Load Article:


class ConsumeLoadArticleAddSched(ConsumeAddDifferBase):
    model_name = 'article'
    cron_string = CONSUMER_LOAD_CRON_STRING
    task_args = ['load', 'article']


class ConsumeLoadArticleUpdateSched(ConsumeUpdateDifferBase):
    model_name = 'article'
    cron_string = CONSUMER_LOAD_CRON_STRING
    task_args = ['load', 'article']


class ConsumeLoadArticleDeleteSched(ConsumeDeleteDifferBase):
    model_name = 'article'
    cron_string = CONSUMER_LOAD_CRON_STRING
    task_args = ['load', 'article']


# Load PressRelease:


class ConsumeLoadPressReleaseAddSched(ConsumeAddDifferBase):
    model_name = 'press_release'
    cron_string = CONSUMER_BLOGS_CRON_STRING
    task_args = ['load', 'press_release']


class ConsumeLoadPressReleaseUpdateSched(ConsumeUpdateDifferBase):
    model_name = 'press_release'
    cron_string = CONSUMER_BLOGS_CRON_STRING
    task_args = ['load', 'press_release']


class ConsumeLoadPressReleaseDeleteSched(ConsumeDeleteDifferBase):
    model_name = 'press_release'
    cron_string = CONSUMER_BLOGS_CRON_STRING
    task_args = ['load', 'press_release']


# Load News:


class ConsumeLoadNewsAddSched(ConsumeAddDifferBase):
    model_name = 'news'
    cron_string = CONSUMER_BLOGS_CRON_STRING
    task_args = ['load', 'news']


class ConsumeLoadNewsUpdateSched(ConsumeUpdateDifferBase):
    model_name = 'news'
    cron_string = CONSUMER_BLOGS_CRON_STRING
    task_args = ['load', 'news']


class ConsumeLoadNewsDeleteSched(ConsumeDeleteDifferBase):
    model_name = 'news'
    cron_string = CONSUMER_BLOGS_CRON_STRING
    task_args = ['load', 'news']


CONSUMER_SCHEDS = {
    'extract': {
        'collection': {
            'add': ConsumeExtractCollectionAddSched,
            'update': ConsumeExtractCollectionUpdateSched,
            'delete': ConsumeExtractCollectionDeleteSched
        },
        'journal': {
            'add': ConsumeExtractJournalAddSched,
            'update': ConsumeExtractJournalUpdateSched,
            'delete': ConsumeExtractJournalDeleteSched
        },
        'issue': {
            'add': ConsumeExtractIssueAddSched,
            'update': ConsumeExtractIssueUpdateSched,
            'delete': ConsumeExtractIssueDeleteSched,
        },
        'article': {
            'add': ConsumeExtractArticleAddSched,
            'update': ConsumeExtractArticleUpdateSched,
            'delete': ConsumeExtractArticleDeleteSched,
        },
        'press_release': {
            'add': ConsumeExtractPressReleaseAddSched,
            'update': ConsumeExtractPressReleaseUpdateSched,
            'delete': ConsumeExtractPressReleaseDeleteSched
        },
        'news': {
            'add': ConsumeExtractNewsAddSched,
            'update': ConsumeExtractNewsUpdateSched,
            'delete': ConsumeExtractNewsDeleteSched
        }
    },
    'transform': {
        'collection': {
            'add': ConsumeTransformCollectionAddSched,
            'update': ConsumeTransformCollectionUpdateSched,
            'delete': ConsumeTransformCollectionDeleteSched
        },
        'journal': {
            'add': ConsumeTransformJournalAddSched,
            'update': ConsumeTransformJournalUpdateSched,
            'delete': ConsumeTransformJournalDeleteSched
        },
        'issue': {
            'add': ConsumeTransformIssueAddSched,
            'update': ConsumeTransformIssueUpdateSched,
            'delete': ConsumeTransformIssueDeleteSched,
        },
        'article': {
            'add': ConsumeTransformArticleAddSched,
            'update': ConsumeTransformArticleUpdateSched,
            'delete': ConsumeTransformArticleDeleteSched,
        },
        'press_release': {
            'add': ConsumeTransformPressReleaseAddSched,
            'update': ConsumeTransformPressReleaseUpdateSched,
            'delete': ConsumeTransformPressReleaseDeleteSched
        },
        'news': {
            'add': ConsumeTransformNewsAddSched,
            'update': ConsumeTransformNewsUpdateSched,
            'delete': ConsumeTransformNewsDeleteSched
        }
    },
    'load': {
        'collection': {
            'add': ConsumeLoadCollectionAddSched,
            'update': ConsumeLoadCollectionUpdateSched,
            'delete': ConsumeLoadCollectionDeleteSched
        },
        'journal': {
            'add': ConsumeLoadJournalAddSched,
            'update': ConsumeLoadJournalUpdateSched,
            'delete': ConsumeLoadJournalDeleteSched
        },
        'issue': {
            'add': ConsumeLoadIssueAddSched,
            'update': ConsumeLoadIssueUpdateSched,
            'delete': ConsumeLoadIssueDeleteSched,
        },
        'article': {
            'add': ConsumeLoadArticleAddSched,
            'update': ConsumeLoadArticleUpdateSched,
            'delete': ConsumeLoadArticleDeleteSched,
        },
        'press_release': {
            'add': ConsumeLoadPressReleaseAddSched,
            'update': ConsumeLoadPressReleaseUpdateSched,
            'delete': ConsumeLoadPressReleaseDeleteSched
        },
        'news': {
            'add': ConsumeLoadNewsAddSched,
            'update': ConsumeLoadNewsUpdateSched,
            'delete': ConsumeLoadNewsDeleteSched
        }
    }
}
