# coding: utf-8
from __future__ import unicode_literals

import uuid
from datetime import datetime
from mongoengine import (
    UUIDField,
    DateTimeField,
    BooleanField,
    StringField,
)


class BaseMixin(object):
    # campos comuns a todos os modelos ETL
    _id = UUIDField(primary_key=True, required=True, default=uuid.uuid4)
    uuid = UUIDField(required=True, default=uuid.uuid4)
    updated_at = DateTimeField()
    is_locked = BooleanField(default=False)

    # soft delete
    is_deleted = BooleanField(required=True, default=False)

    # campos genericos do processamento:
    process_start_at = DateTimeField()
    process_finish_at = DateTimeField()
    process_completed = BooleanField(required=True, default=False)
    process_error_msg = StringField()

    @property
    def has_errors(self):
        """
        Retorna True se o documento poduziu algum error
        na fase de extração.
        """
        if hasattr(self, 'process_error_msg'):
            return self.process_error_msg.strip() == ""
        else:
            return False

    # reset:
    def reset(self):
        """
        Restaura os campos de controle do documento
        ao ponto anterior à extração
        """
        self.process_start_at = None
        self.process_finish_at = None
        self.process_completed = False
        self.process_error_msg = ''

    @classmethod  # signal pre_save (asociar em cada modelo)
    def pre_save(cls, sender, document, **kwargs):
        document.updated_at = datetime.now()

    def __unicode__(self):
        return unicode(self._id)
