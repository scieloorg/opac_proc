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


class BaseDynamicDocument(DynamicDocument):
    # campos relacionados a extração
    extraction_start_at = DateTimeField()
    extraction_finish_at = DateTimeField()
    extraction_complete = BooleanField(required=True, default=False)
    extraction_error_msg = StringField()

    # campos relacionados a transformação
    transform_start_at = DateTimeField()
    transform_finish_at = DateTimeField()
    transform_complete = BooleanField(required=True, default=False)
    transform_error_msg = StringField()

    # campos relacionados a carga
    loading_start_at = DateTimeField()
    loading_finish_at = DateTimeField()
    loading_complete = BooleanField(required=True, default=False)
    loading_error_msg = StringField()

    # soft delete
    is_deleted = BooleanField(required=True, default=False)

    meta = {'allow_inheritance': True}


    @property
    def is_extracting(self):
        """
        Retorna True se o documento esta em fase de extração
        """
        return not self.transform_complete

    @property
    def is_transforming(self):
        """
        Retorna True se o documento esta em fase de transformação
        """
        return not self.extraction_complete

    @property
    def is_loading(self):
        """
        Retorna True se o documento esta em fase de carga
        """
        return not self.loading_complete

    @property
    def has_extraction_error(self):
        """
        Retorna True se o documento poduziu algum error
        na fase de extração.
        """
        if hasattr(self, 'extraction_error_msg'):
            return self.extraction_error_msg.strip() == ""
        else:
            return False

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

    # reset:
    def reset_for_extraction(self):
        """
        Restaura os campos de controle do documento
        ao ponto anterior à extração
        """
        self.extraction_start_at = None
        self.extraction_finish_at = None
        self.extraction_complete = False
        self.extraction_error_msg = ''
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

    def reset_for_loading(self):
        """
        Restaura os campos de controle do documento
        ao ponto anterior à carga
        """
        self.loading_start_at = None
        self.loading_finish_at = None
        self.loading_complete = False
        self.loading_error_msg = ''
