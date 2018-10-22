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


class BaseIdModel(object):
    _id = UUIDField(primary_key=True, required=True, default=uuid.uuid4)
    uuid = UUIDField(required=True, default=uuid.uuid4, unique=True)
    collection_acronym = StringField(max_length=5, required=True, default=config.OPAC_PROC_COLLECTION)
    # campos de controle:
    created_at = DateTimeField()
    updated_at = DateTimeField()
    # processing_date do AM:
    processing_date = DateTimeField(null=True)
    # datas de excecução de ex, tr e lo.
    extract_execution_date = DateTimeField(null=True)
    transform_execution_date = DateTimeField(null=True)
    load_execution_date = DateTimeField(null=True)

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um DiffModel
        """
        raise NotImplementedError('deve implementar este metodo em cada modelo')

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
        return super(BaseIdModel, self).save(*args, **kwargs)


class CollectionIdModel(BaseIdModel, Document):
    meta = {
        'collection': 'identifiers_collection',
        'indexes': [
            'uuid',
            'collection_acronym',
            'processing_date',
        ]
    }

    def __unicode__(self):
        return self.collection_acronym

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um CollectionDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': self.collection_acronym,
        }


class JournalIdModel(BaseIdModel, Document):
    journal_issn = StringField(max_length=10, required=True)

    meta = {
        'collection': 'identifiers_journal',
        'indexes': [
            'uuid',
            'collection_acronym',
            'journal_issn',
            'processing_date',
        ]
    }

    def __unicode__(self):
        return self.journal_issn

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um JournalDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': self.collection_acronym,
            'journal_issn': self.journal_issn
        }


class IssueIdModel(BaseIdModel, Document):
    journal_issn = StringField(max_length=10, required=True)
    issue_pid = StringField(max_length=20, required=True)

    meta = {
        'collection': 'identifiers_issue',
        'indexes': [
            'uuid',
            'collection_acronym',
            'journal_issn',
            'issue_pid',
            'processing_date',
        ]
    }

    def __unicode__(self):
        return self.issue_pid

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um IssueDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': self.collection_acronym,
            'journal_issn': self.journal_issn,
            'issue_pid': self.issue_pid
        }


class ArticleIdModel(BaseIdModel, Document):
    journal_issn = StringField(max_length=10, required=True)
    issue_pid = StringField(max_length=20, required=True)
    article_pid = StringField(max_length=25, required=True)

    meta = {
        'collection': 'identifiers_article',
        'indexes': [
            'uuid',
            'collection_acronym',
            'journal_issn',
            'issue_pid',
            'article_pid',
            'processing_date',
        ]
    }

    def __unicode__(self):
        return self.article_pid

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um ArticleDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': self.collection_acronym,
            'journal_issn': self.journal_issn,
            'issue_pid': self.issue_pid,
            'article_pid': self.article_pid
        }


class NewsIdModel(BaseIdModel, Document):
    url_id = StringField(max_length=256, required=True)

    meta = {
        'collection': 'identifiers_news',
        'indexes': [
            'uuid',
            'collection_acronym',
            'url_id',
            'processing_date',
        ]
    }

    def __unicode__(self):
        return "[lang: %s] url: %s" % (self.lang, self.url_id)

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um NewsDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': self.collection_acronym,
            'url_id': self.url_id
        }


class PressReleaseIdModel(BaseIdModel, Document):
    url_id = StringField(max_length=256, required=True)

    meta = {
        'collection': 'identifiers_press_release',
        'indexes': [
            'uuid',
            'collection_acronym',
            'url_id',
            'processing_date',
        ]
    }

    def __unicode__(self):
        return self.url_id

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um PressReleaseDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': self.collection_acronym,
            'url_id': self.url_id
        }
