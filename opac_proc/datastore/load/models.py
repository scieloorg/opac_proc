# coding: utf-8
from __future__ import unicode_literals

from mongoengine import (
    DynamicDocument,
    StringField,
    IntField,
    DateTimeField,
    ListField,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    ReferenceField,
    BooleanField,
    URLField,
)


class BaseLoadMixin(object):

    # campos relacionados a carga
    loading_start_at = DateTimeField()
    loading_finish_at = DateTimeField()
    loading_complete = BooleanField(required=True, default=False)
    loading_error_msg = StringField()

    # soft delete
    is_deleted = BooleanField(required=True, default=False)

    @property
    def is_loading(self):
        """
        Retorna True se o documento esta em fase de carga
        """
        return not self.loading_complete

    @property
    def has_loading_error(self):
        """
        Retorna True se o documento poduziu algum error
        na fase de carga.
        """
        if hasattr(self, 'loading_error_msg'):
            return self.loading_error_msg.strip() == ""
        else:
            return False

    def reset_for_loading(self):
        """
        Restaura os campos de controle do documento
        ao ponto anterior à carga
        """
        self.loading_start_at = None
        self.loading_finish_at = None
        self.loading_complete = False
        self.loading_error_msg = ''


class ExtractCollection(BaseLoadMixin, BaseDynamicDocument):
    pass


class ExtractJournal(BaseLoadMixin, BaseDynamicDocument):
    pass


class Issue(BaseLoadMixin, BaseDynamicDocument):
    pass


class Article(BaseLoadMixin, BaseDynamicDocument):
    pass
