# coding: utf-8
import uuid
from datetime import datetime

from mongoengine import (
    Document,
    UUIDField,
    StringField,
    DateTimeField,
)

from opac_proc.web import config


class BaseDiffModel(object):
    _id = UUIDField(primary_key=True, required=True, default=uuid.uuid4)
    uuid = UUIDField(required=True, default=uuid.uuid4)
    stage = StringField(max_length=20, required=True, default='default')  # ex: 'extact' | 'transform' | 'load'
    collection_acronym = StringField(max_length=5, required=True, default=config.OPAC_PROC_COLLECTION)
    # campos de controle:
    created_at = DateTimeField()
    updated_at = DateTimeField()
    # ação a realizar: ADD | UPDATE | DELETE
    action = StringField(max_length=20)
    done_at = DateTimeField()

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
        return super(BaseDiffModel, self).save(*args, **kwargs)


class CollectionDiffModel(BaseDiffModel, Document):
    meta = {
        'collection': 'diff_collection',
        'indexes': [
            'uuid',
            'collection_acronym',
            'action',
            'done_at',
        ]
    }

    def __unicode__(self):
        return self.collection_acronym


class JournalDiffModel(BaseDiffModel, Document):
    journal_issn = StringField(max_length=10, required=True)

    meta = {
        'collection': 'diff_journal',
        'indexes': [
            'uuid',
            'collection_acronym',
            'journal_issn',
            'action',
            'done_at',
        ]
    }

    def __unicode__(self):
        return self.journal_issn


class IssueDiffModel(BaseDiffModel, Document):
    journal_issn = StringField(max_length=10, required=True)
    issue_pid = StringField(max_length=20, required=True)

    meta = {
        'collection': 'diff_issue',
        'indexes': [
            'uuid',
            'collection_acronym',
            'journal_issn',
            'issue_pid',
            'action',
            'done_at',
        ]
    }

    def __unicode__(self):
        return self.issue_pid


class ArticleDiffModel(BaseDiffModel, Document):
    journal_issn = StringField(max_length=10, required=True)
    issue_pid = StringField(max_length=20, required=True)
    article_pid = StringField(max_length=25, required=True)

    meta = {
        'collection': 'diff_article',
        'indexes': [
            'uuid',
            'collection_acronym',
            'journal_issn',
            'issue_pid',
            'article_pid',
            'action',
            'done_at',
        ]
    }

    def __unicode__(self):
        return self.article_pid


class NewsDiffModel(BaseDiffModel, Document):
    url_id = StringField(max_length=256, required=True)

    meta = {
        'collection': 'diff_news',
        'indexes': [
            'uuid',
            'collection_acronym',
            'url_id',
            'action',
            'done_at',
        ]
    }

    def __unicode__(self):
        return "[lang: %s] url: %s" % (self.lang, self.url_id)


class PressReleaseDiffModel(BaseDiffModel, Document):
    url_id = StringField(max_length=256, required=True)

    meta = {
        'collection': 'diff_press_release',
        'indexes': [
            'uuid',
            'collection_acronym',
            'url_id',
            'action',
            'done_at',
        ]
    }

    def __unicode__(self):
        return self.url_id
