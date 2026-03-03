# coding:utf-8

from flask_testing import TestCase
from mongoengine import disconnect
from opac_proc.web.webapp import create_app


class BaseTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super(BaseTestCase, self).__init__(*args, **kwargs)

    def create_app(self):
        disconnect(alias="default")
        app = create_app(test_mode=True)
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        return app
