# coding: utf-8
import os
import sys


import rq_dashboard
import rq_scheduler_dashboard

from flask import Flask
from flask import render_template, flash  # redirect,
from flask_mongoengine import MongoEngine
from flask_wtf import Form
from flask_debugtoolbar import DebugToolbarExtension
from flask_admin import Admin
from flask_admin.contrib.mongoengine import ModelView

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.datastore.extract.models import ExtractCollection, ExtractJournal, ExtractIssue, ExtractArticle
from opac_proc.datastore.transform.models import TransformCollection, TransformJournal, TransformIssue, TransformArticle
from opac_proc.datastore.load.models import LoadCollection, LoadJournal, LoadIssue, LoadArticle

db = MongoEngine()
toolbar = DebugToolbarExtension()

app = Flask(
    __name__,
    static_url_path='/static',
    static_folder='static',
    instance_relative_config=False)

app.config.from_object(rq_dashboard.default_settings)
app.config.from_object(rq_scheduler_dashboard.default_settings)
app.config.from_pyfile('config.py')

app.register_blueprint(rq_scheduler_dashboard.blueprint, url_prefix='/scheduler')
app.register_blueprint(rq_dashboard.blueprint, url_prefix='/dashboard')

db.init_app(app)

admin = Admin(app, name='OPAC Proc Admin', template_mode='bootstrap3')
# Extract views:
admin.add_view(ModelView(ExtractCollection, category='Extraction', name='Collection'))
admin.add_view(ModelView(ExtractJournal, category='Extraction', name='Journal'))
admin.add_view(ModelView(ExtractIssue, category='Extraction', name='Issue'))
admin.add_view(ModelView(ExtractArticle, category='Extraction', name='Article'))
# Transform view:
admin.add_view(ModelView(TransformCollection, category='Transform', name='Collection'))
admin.add_view(ModelView(TransformJournal, category='Transform', name='Journal'))
admin.add_view(ModelView(TransformIssue, category='Transform', name='Issue'))
admin.add_view(ModelView(TransformArticle, category='Transform', name='Article'))
# Transform view:
admin.add_view(ModelView(LoadCollection, category='Load', name='Collection'))
admin.add_view(ModelView(LoadJournal, category='Load', name='Journal'))
admin.add_view(ModelView(LoadIssue, category='Load', name='Issue'))
admin.add_view(ModelView(LoadArticle, category='Load', name='Article'))


@app.route('/', methods=('GET', 'POST'))
def home():
    extract_collection_count = ExtractCollection.objects.all().count()
    extract_journal_count = ExtractJournal.objects.all().count()
    extract_issue_count = ExtractIssue.objects.all().count()
    extract_article_count = ExtractArticle.objects.all().count()

    transform_collection_count = TransformCollection.objects.all().count()
    transform_journal_count = TransformJournal.objects.all().count()
    transform_issue_count = TransformIssue.objects.all().count()
    transform_article_count = TransformArticle.objects.all().count()

    load_collection_count = LoadCollection.objects.all().count()
    load_journal_count = LoadJournal.objects.all().count()
    load_issue_count = LoadIssue.objects.all().count()
    load_article_count = LoadArticle.objects.all().count()

    context = {
        # extract
        'extract_collection_count': extract_collection_count,
        'extract_journal_count': extract_journal_count,
        'extract_issue_count': extract_issue_count,
        'extract_article_count': extract_article_count,
        # tranform
        'transform_collection_count': transform_collection_count,
        'transform_journal_count': transform_journal_count,
        'transform_issue_count': transform_issue_count,
        'transform_article_count': transform_article_count,
        # load
        'load_collection_count': load_collection_count,
        'load_journal_count': load_journal_count,
        'load_issue_count': load_issue_count,
        'load_article_count': load_article_count,
    }
    return render_template("home.html", **context)


@app.route('/extract/', methods=('GET', 'POST'))
@app.route('/extract', methods=('GET', 'POST'))
def extract():
    context = {}
    return render_template("extract.html", **context)


@app.route('/transform/', methods=('GET', 'POST'))
@app.route('/transform', methods=('GET', 'POST'))
def transform():
    context = {}
    return render_template("transform.html", **context)


@app.route('/load/', methods=('GET', 'POST'))
@app.route('/load', methods=('GET', 'POST'))
def load():
    context = {}
    return render_template("load.html", **context)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8001)
