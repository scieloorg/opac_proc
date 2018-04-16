# coding: utf-8
import uuid
from datetime import datetime

from mongoengine import (
    DynamicDocument,
    UUIDField,
    StringField,
    DateTimeField,
)


class BaseEventModel(object):
    _id = UUIDField(primary_key=True, required=True, default=uuid.uuid4)
    description = StringField(required=True)
    created_at = DateTimeField(default=datetime.now)


class SyncEventModel(BaseEventModel, DynamicDocument):
    meta = {
        'collection': 'events_sync',
        'ordering': ['-created_at']
    }

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()

        return super(SyncEventModel, self).save(*args, **kwargs)
