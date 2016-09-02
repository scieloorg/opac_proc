# coding: utf-8
from __future__ import unicode_literals

from mongoengine import DynamicDocument, signals
from opac_proc.datastore.base_mixin import BaseMixin


class LoadCollection(BaseMixin, DynamicDocument):
    meta = {
        'collection': 'l_collection'
    }
signals.pre_save.connect(LoadCollection.pre_save, sender=LoadCollection)


class LoadJournal(BaseMixin, DynamicDocument):
    meta = {
        'collection': 'l_journal'
    }
signals.pre_save.connect(LoadJournal.pre_save, sender=LoadJournal)


class LoadIssue(BaseMixin, DynamicDocument):
    meta = {
        'collection': 'l_issue'
    }
signals.pre_save.connect(LoadIssue.pre_save, sender=LoadIssue)


class LoadArticle(BaseMixin, DynamicDocument):
    meta = {
        'collection': 'l_article'
    }
signals.pre_save.connect(LoadArticle.pre_save, sender=LoadArticle)
