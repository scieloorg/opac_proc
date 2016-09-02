# coding: utf-8
from __future__ import unicode_literals

from mongoengine import DynamicDocument, signals
from opac_proc.datastore.base_mixin import BaseMixin


class TransformCollection(BaseMixin, DynamicDocument):
    meta = {
        'collection': 't_collection'
    }
signals.pre_save.connect(TransformCollection.pre_save, sender=TransformCollection)


class TransformJournal(BaseMixin, DynamicDocument):
    meta = {
        'collection': 't_journal'
    }
signals.pre_save.connect(TransformJournal.pre_save, sender=TransformJournal)


class TransformIssue(BaseMixin, DynamicDocument):
    meta = {
        'collection': 't_issue'
    }
signals.pre_save.connect(TransformIssue.pre_save, sender=TransformIssue)


class TransformArticle(BaseMixin, DynamicDocument):
    meta = {
        'collection': 't_article'
    }
signals.pre_save.connect(TransformArticle.pre_save, sender=TransformArticle)
