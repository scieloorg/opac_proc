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
from flask_mail import Mail

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.web import urls

db = MongoEngine()
toolbar = DebugToolbarExtension()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'accounts.login'
mail = Mail()


def register_extensions(app):
    from accounts.handlers import *   # NOQA
    login_manager.init_app(app)
    db.init_app(app)
    app.session_interface = MongoEngineSessionInterface(db)
    toolbar.init_app(app)
    mail.init_app(app)


def regiter_bluprints(app):
    from accounts import accounts
    from accounts.helpers import check_user_logged_in_or_redirect
    rq_scheduler_dashboard.blueprint.before_request(check_user_logged_in_or_redirect)
    rq_dashboard.blueprint.before_request(check_user_logged_in_or_redirect)
    app.register_blueprint(accounts)
    app.register_blueprint(rq_scheduler_dashboard.blueprint, url_prefix='/scheduler')
    app.register_blueprint(rq_dashboard.blueprint, url_prefix='/dashboard')


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

    # init extensions
    register_extensions(app)
    # blueprints
    regiter_bluprints(app)

    app.wsgi_app = ProxyFix(app.wsgi_app)
    urls.add_url_rules(app)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
