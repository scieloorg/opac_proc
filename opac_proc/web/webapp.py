# coding: utf-8
import os
import sys

import rq_dashboard
import rq_scheduler_dashboard

from flask import Flask

from flask import render_template, flash
from flask_mongoengine import MongoEngine
from flask_wtf import Form
from flask_debugtoolbar import DebugToolbarExtension

from mongoengine.context_managers import switch_db
from opac_schema.v1.models import Collection as OpacCollection
from opac_schema.v1.models import Journal as OpacJournal
from opac_schema.v1.models import Issue as OpacIssue
from opac_schema.v1.models import Article as OpacArticle
from opac_schema.v1.models import PressRelease as OpacPressRelease
from opac_schema.v1.models import Sponsor as OpacSponsor
from opac_schema.v1.models import Pages as OpacPages
from opac_schema.v1.models import Resource as OpacResource
from opac_schema.v1.models import News as OpacNews

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.web.views.extract.list_views import (
    ExtractCollectionListView,
    ExtractJournalListView,
    ExtractIssueListView,
    ExtractArticleListView,
    ExtractLogListView)

from opac_proc.web.views.extract.detail_views import (
    ExtractCollectionDetailView,
    ExtractJournalDetailView,
    ExtractIssueDetailView,
    ExtractArticleDetailView,
    ExtractLogDetailView)

from opac_proc.web.views.transform.list_views import (
    TransformCollectionListView,
    TransformJournalListView,
    TransformIssueListView,
    TransformArticleListView,
    TransformLogListView)

from opac_proc.web.views.transform.detail_views import (
    TransformCollectionDetailView,
    TransformJournalDetailView,
    TransformIssueDetailView,
    TransformArticleDetailView,
    TransformLogDetailView)


from opac_proc.web.views.load.list_views import (
    LoadCollectionListView,
    LoadJournalListView,
    LoadIssueListView,
    LoadArticleListView,
    LoadLogListView)

from opac_proc.web.views.load.detail_views import (
    LoadCollectionDetailView,
    LoadJournalDetailView,
    LoadIssueDetailView,
    LoadArticleDetailView,
    LoadLogDetailView)

from opac_proc.datastore import models
from opac_proc.datastore.mongodb_connector import register_connections, get_opac_webapp_db_name

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
toolbar.init_app(app)

register_connections()
OPAC_WEBAPP_DB_NAME = get_opac_webapp_db_name()


@app.route('/', methods=('GET', 'POST'))
def home():
    extract_collection_count = models.ExtractCollection.objects.all().count()
    extract_journal_count = models.ExtractJournal.objects.all().count()
    extract_issue_count = models.ExtractIssue.objects.all().count()
    extract_article_count = models.ExtractArticle.objects.all().count()

    transform_collection_count = models.TransformCollection.objects.all().count()
    transform_journal_count = models.TransformJournal.objects.all().count()
    transform_issue_count = models.TransformIssue.objects.all().count()
    transform_article_count = models.TransformArticle.objects.all().count()

    load_collection_count = models.LoadCollection.objects.all().count()
    load_journal_count = models.LoadJournal.objects.all().count()
    load_issue_count = models.LoadIssue.objects.all().count()
    load_article_count = models.LoadArticle.objects.all().count()

    with switch_db(OpacCollection, OPAC_WEBAPP_DB_NAME):
        opac_collection_count = OpacCollection.objects.all().count()

    with switch_db(OpacJournal, OPAC_WEBAPP_DB_NAME):
        opac_journal_count = OpacJournal.objects.all().count()

    with switch_db(OpacIssue, OPAC_WEBAPP_DB_NAME):
        opac_issue_count = OpacIssue.objects.all().count()

    with switch_db(OpacArticle, OPAC_WEBAPP_DB_NAME):
        opac_article_count = OpacArticle.objects.all().count()

    with switch_db(OpacSponsor, OPAC_WEBAPP_DB_NAME):
        opac_sponsor_count = OpacSponsor.objects.all().count()

    with switch_db(OpacPages, OPAC_WEBAPP_DB_NAME):
        opac_page_count = OpacPages.objects.all().count()

    with switch_db(OpacResource, OPAC_WEBAPP_DB_NAME):
        opac_resource_count = OpacResource.objects.all().count()

    with switch_db(OpacNews, OPAC_WEBAPP_DB_NAME):
        opac_news_count = OpacNews.objects.all().count()

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
        # opac
        'opac_collection_count': opac_collection_count,
        'opac_journal_count': opac_journal_count,
        'opac_issue_count': opac_issue_count,
        'opac_article_count': opac_article_count,
        # opac outros modelos
        'opac_sponsor_count': opac_sponsor_count,
        'opac_page_count': opac_page_count,
        'opac_resource_count': opac_resource_count,
        'opac_news_count': opac_news_count,
    }
    return render_template("home.html", **context)

# EXTRACT: List View

app.add_url_rule(
    '/extract/collections/',
    view_func=ExtractCollectionListView.as_view('extract_collections_list'))

app.add_url_rule(
    '/extract/journals/',
    view_func=ExtractJournalListView.as_view('extract_journals_list'))

app.add_url_rule(
    '/extract/issues/',
    view_func=ExtractIssueListView.as_view('extract_issues_list'))

app.add_url_rule(
    '/extract/articles/',
    view_func=ExtractArticleListView.as_view('extract_articles_list'))

app.add_url_rule(
    '/extract/logs/',
    view_func=ExtractLogListView.as_view('extract_logs_list'))

# EXTRACT: Detail View

app.add_url_rule(
    '/extract/collections/<string:object_id>/',
    view_func=ExtractCollectionDetailView.as_view('extract_collection_detail'),
    methods=['GET'])

app.add_url_rule(
    '/extract/journals/<string:object_id>/',
    view_func=ExtractJournalDetailView.as_view('extract_journal_detail'),
    methods=['GET'])

app.add_url_rule(
    '/extract/issues/<string:object_id>/',
    view_func=ExtractIssueDetailView.as_view('extract_issue_detail'),
    methods=['GET'])

app.add_url_rule(
    '/extract/articles/<string:object_id>/',
    view_func=ExtractArticleDetailView.as_view('extract_article_detail'),
    methods=['GET'])

app.add_url_rule(
    '/extract/logs/<string:object_id>/',
    view_func=ExtractLogDetailView.as_view('extract_log_detail'),
    methods=['GET'])

# TRANSFORM: List Views

app.add_url_rule(
    '/transform/collections/',
    view_func=TransformCollectionListView.as_view('transform_collections_list'))

app.add_url_rule(
    '/transform/journals/',
    view_func=TransformJournalListView.as_view('transform_journals_list'))

app.add_url_rule(
    '/transform/issues/',
    view_func=TransformIssueListView.as_view('transform_issues_list'))

app.add_url_rule(
    '/transform/articles/',
    view_func=TransformArticleListView.as_view('transform_articles_list'))

app.add_url_rule(
    '/transform/logs/',
    view_func=TransformLogListView.as_view('transform_logs_list'))


# TRANSFORM: Detail View

app.add_url_rule(
    '/transform/collections/<string:object_id>/',
    view_func=TransformCollectionDetailView.as_view('transform_collection_detail'),
    methods=['GET'])

app.add_url_rule(
    '/transform/journals/<string:object_id>/',
    view_func=TransformJournalDetailView.as_view('transform_journal_detail'),
    methods=['GET'])

app.add_url_rule(
    '/transform/issues/<string:object_id>/',
    view_func=TransformIssueDetailView.as_view('transform_issue_detail'),
    methods=['GET'])

app.add_url_rule(
    '/transform/articles/<string:object_id>/',
    view_func=TransformArticleDetailView.as_view('transform_article_detail'),
    methods=['GET'])

app.add_url_rule(
    '/transform/logs/<string:object_id>/',
    view_func=TransformLogDetailView.as_view('transform_log_detail'),
    methods=['GET'])

# LOAD: List View

app.add_url_rule(
    '/load/collections/',
    view_func=LoadCollectionListView.as_view('load_collections'))

app.add_url_rule(
    '/load/journals/',
    view_func=LoadJournalListView.as_view('load_journals'))

app.add_url_rule(
    '/load/issues/',
    view_func=LoadIssueListView.as_view('load_issues'))

app.add_url_rule(
    '/load/articles/',
    view_func=LoadArticleListView.as_view('load_articles'))

app.add_url_rule(
    '/load/logs/',
    view_func=LoadLogListView.as_view('load_logs_list'))
# Load: Detail View

app.add_url_rule(
    '/load/collections/<string:object_id>/',
    view_func=LoadCollectionDetailView.as_view('load_collection_detail'),
    methods=['GET'])

app.add_url_rule(
    '/load/journals/<string:object_id>/',
    view_func=LoadJournalDetailView.as_view('load_journal_detail'),
    methods=['GET'])

app.add_url_rule(
    '/load/issues/<string:object_id>/',
    view_func=LoadIssueDetailView.as_view('load_issue_detail'),
    methods=['GET'])

app.add_url_rule(
    '/load/articles/<string:object_id>/',
    view_func=LoadArticleDetailView.as_view('load_article_detail'),
    methods=['GET'])

app.add_url_rule(
    '/load/logs/<string:object_id>/',
    view_func=LoadLogDetailView.as_view('load_log_detail'),
    methods=['GET'])


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8001)
