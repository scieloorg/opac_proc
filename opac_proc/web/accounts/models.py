# coding: utf-8
from datetime import datetime
from mongoengine import (
    Document,
    EmailField,
    StringField,
    BooleanField,
    DateTimeField)


class User(Document):
    email = EmailField(unique=True)
    password = StringField(default=True)
    active = BooleanField(default=True)
    timestamp = DateTimeField(default=datetime.now())
    email_confirmed = BooleanField(default=False)
