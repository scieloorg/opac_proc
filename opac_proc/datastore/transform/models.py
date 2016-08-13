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


class BaseExtractionMixin(object):

    # # campos relacionados a transformação
    transform_start_at = DateTimeField()
    transform_finish_at = DateTimeField()
    transform_complete = BooleanField(required=True, default=False)
    transform_error_msg = StringField()

    # soft delete
    is_deleted = BooleanField(required=True, default=False)

    @property
    def is_transforming(self):
        """
        Retorna True se o documento esta em fase de transformação
        """
        return not self.extraction_complete

    @property
    def has_transform_error(self):
        """
        Retorna True se o documento poduziu algum error
        na fase de transformação.
        """
        if hasattr(self, 'transform_error_msg'):
            return self.transform_error_msg.strip() == ""
        else:
            return False

    def reset_for_transform(self):
        """
        Restaura os campos de controle do documento
        ao ponto anterior à transformação
        """
        # tranformação:
        self.transform_start_at = None
        self.transform_finish_at = None
        self.transform_complete = False
        self.transform_error_msg = ''
        # carga:
        self.loading_start_at = None
        self.loading_finish_at = None
        self.loading_complete = False
        self.loading_error_msg = ''


class ExtractCollection(BaseExtractionMixin, BaseDynamicDocument):
    pass


class ExtractJournal(BaseExtractionMixin, BaseDynamicDocument):
    pass


class Issue(BaseExtractionMixin, BaseDynamicDocument):
    pass


class Article(BaseExtractionMixin, BaseDynamicDocument):
    pass
