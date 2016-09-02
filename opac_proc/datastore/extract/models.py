# coding: utf-8
from __future__ import unicode_literals

from mongoengine import DynamicDocument, signals
from opac_proc.datastore.base_mixin import BaseMixin


class ExtractCollection(BaseMixin, DynamicDocument):
    meta = {
        'collection': 'e_collection'
    }
signals.pre_save.connect(ExtractCollection.pre_save, sender=ExtractCollection)


class ExtractJournal(BaseMixin, DynamicDocument):
    meta = {
        'collection': 'e_journal'
    }
signals.pre_save.connect(ExtractCollection.pre_save, sender=ExtractJournal)


class ExtractIssue(BaseMixin, DynamicDocument):
    meta = {
        'collection': 'e_issue'
    }
signals.pre_save.connect(ExtractCollection.pre_save, sender=ExtractIssue)


class ExtractArticle(BaseMixin, DynamicDocument):
    meta = {
        'collection': 'e_article'
    }
signals.pre_save.connect(ExtractCollection.pre_save, sender=ExtractArticle)
