# coding:utf-8
import time
import tempfile

import pymongo
from flask import current_app
from flask_testing import TestCase


class BaseTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super(BaseTestCase, self).__init__(*args, **kwargs)

    def create_app(self):
        app = current_app
        app.config['TESTING'] = True
        return app
