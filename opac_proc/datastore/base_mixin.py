# coding: utf-8
from __future__ import unicode_literals

import uuid
from datetime import datetime
from mongoengine import (
    UUIDField,
    DateTimeField,
    BooleanField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    DynamicEmbeddedDocument
)


class ProcessMetada(EmbeddedDocument):
    updated_at = DateTimeField(default=datetime.now)
    process_start_at = DateTimeField()
    process_finish_at = DateTimeField()
    process_completed = BooleanField(required=True, default=False)
    must_reprocess = BooleanField(required=True, default=False)


class LoadedData(DynamicEmbeddedDocument):
    pass


class BaseMixin(object):
    # campos comuns a todos os modelos ETL
    _id = UUIDField(primary_key=True, required=True, default=uuid.uuid4)
    uuid = UUIDField(required=True, default=uuid.uuid4)

    metadata = EmbeddedDocumentField(ProcessMetada)

    @classmethod  # signal pre_save (asociar em cada modelo)
    def pre_save(cls, sender, document, **kwargs):
        document['metadata']['updated_at'] = datetime.now()

    def update_reprocess_field(self, uuid):
        """
        deve ser redefinido em cada subclasse.
        uuid é o campo para identificar qual documento deve ser atualizado.
        """
        raise NotImplementedError

    def update_identifier_model(self, uuid):
        """
        deve ser redefinido em cada subclasse.
        - pegamos o parametro uuid
        - procuramos o modelo na base: identifiers_XYZ correspondente pelo uuid
        - atualizamos as datas de: extração, transformação e carga
          chamando source_sync/populate_jobs# task_populate_one_XYZ(uuid)
        """
        raise NotImplementedError

    @classmethod  # signal pre_save (asociar em cada modelo)
    def post_save(cls, sender, document, **kwargs):
        uuid = document.uuid
        if uuid:
            if document['metadata']['process_completed']:
                # atualizamos as datas de processamento no
                # modelo identifiers só se tiver terminando o processamento
                updated_at = document['metadata']['process_finish_at']
                document.update_identifier_model(uuid, updated_at)
            if document['metadata']['must_reprocess']:
                # notificamos o modelo que tem que ser reprocessando
                document.update_reprocess_field(uuid)

    def __unicode__(self):
        return unicode(self._id)
