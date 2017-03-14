# coding: utf-8
import os
import sys

import rq_dashboard
import rq_scheduler_dashboard

from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, request, flash, redirect, url_for
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, current_user

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.web import urls
from opac_proc.accounts import accounts as accounts_bp

db = MongoEngine()
toolbar = DebugToolbarExtension()
login_manager = LoginManager()


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

    # login
    from opac_proc.accounts.handlers import *  # NOQA vem aqui: check_user_logged_in_or_redirect
    login_manager.session_protection = 'strong'
    login_manager.login_view = 'accounts.login'
    login_manager.init_app(app)

    db.init_app(app)
    # http://docs.mongoengine.org/projects/flask-mongoengine/en/latest/#session-interface
    app.session_interface = MongoEngineSessionInterface(db)
    toolbar.init_app(app)

    # blueprints
    rq_scheduler_dashboard.blueprint.before_request(check_user_logged_in_or_redirect)
    rq_dashboard.blueprint.before_request(check_user_logged_in_or_redirect)
    app.register_blueprint(accounts_bp)
    app.register_blueprint(rq_scheduler_dashboard.blueprint, url_prefix='/scheduler')
    app.register_blueprint(rq_dashboard.blueprint, url_prefix='/dashboard')

    app.wsgi_app = ProxyFix(app.wsgi_app)
    urls.add_url_rules(app)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
