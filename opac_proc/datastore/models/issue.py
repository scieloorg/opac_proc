# coding: utf-8
from __future__ import unicode_literals

from mongoengine import (
    DynamicDocument,
    EmbeddedDocument,
    # campos:
    StringField,
    IntField,
    DateTimeField,
    ListField,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    ReferenceField,
    BooleanField,
    URLField,
    # reverse_delete_rule:
    PULL,
    CASCADE,
    # signals
    signals,
)

from .base import BaseDynamicDocument


class Issue(BaseDynamicDocument):

    meta = {
        'collection': 'issue'
    }
