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

    # campos genericos do processamento:
    process_start_at = DateTimeField()
    process_finish_at = DateTimeField()
    process_completed = BooleanField(required=True, default=False)
    must_reprocess = BooleanField(required=True, default=False)

    @classmethod  # signal pre_save (asociar em cada modelo)
    def pre_save(cls, sender, document, **kwargs):
        document.updated_at = datetime.now()

    def update_reprocess_field(self, uuid):
        """
        deve ser redefinido em cada subclasse.
        uuid é o campo para identificar qual documento deve ser atualizado.
        """
        raise NotImplemented

    @classmethod  # signal pre_save (asociar em cada modelo)
    def post_save(cls, sender, document, **kwargs):
        uuid = document.uuid
        if uuid and document.must_reprocess:
            # notificamos o modelo que tem que ser reprocessando
            return document.update_reprocess_field(uuid)

    def __unicode__(self):
        return unicode(self._id)
