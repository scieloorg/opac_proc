# coding: utf-8
import os
import sys

import rq_dashboard
import rq_scheduler_dashboard

from werkzeug.contrib.fixers import ProxyFix
from flask import Flask
from flask_mongoengine import MongoEngine
from flask_debugtoolbar import DebugToolbarExtension

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.web import urls

db = MongoEngine()
toolbar = DebugToolbarExtension()


def create_app(test_mode=False):
    app = Flask(
        __name__,
        static_url_path='/static',
        static_folder='static',
        instance_relative_config=False)

    app.config.from_object(rq_dashboard.default_settings)
    app.config.from_object(rq_scheduler_dashboard.default_settings)
    app.config.from_pyfile('config.py')

    if test_mode:
        # sobreescrita de conf para testing
        app.config.from_pyfile('config_testing.py')
        app.config['TESTING'] = True
        app.config['DEBUG'] = False

    app.register_blueprint(rq_scheduler_dashboard.blueprint, url_prefix='/scheduler')
    app.register_blueprint(rq_dashboard.blueprint, url_prefix='/dashboard')

    db.init_app(app)
    toolbar.init_app(app)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    urls.add_url_rules(app)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
