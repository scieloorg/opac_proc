# coding: utf-8
from flask import render_template

from mongoengine.context_managers import switch_db
from opac_schema.v1.models import Collection as OpacCollection
from opac_schema.v1.models import Journal as OpacJournal
from opac_schema.v1.models import Issue as OpacIssue
from opac_schema.v1.models import Article as OpacArticle
from opac_schema.v1.models import PressRelease as OpacPressRelease
from opac_schema.v1.models import Sponsor as OpacSponsor
from opac_schema.v1.models import Pages as OpacPages
from opac_schema.v1.models import News as OpacNews

from opac_proc.datastore.mongodb_connector import register_connections, get_opac_webapp_db_name
from opac_proc.datastore import models


def home():
    register_connections()
    OPAC_WEBAPP_DB_NAME = get_opac_webapp_db_name()
    # extract counts
    extract_collection_count = models.ExtractCollection.objects.all().count()
    extract_journal_count = models.ExtractJournal.objects.all().count()
    extract_issue_count = models.ExtractIssue.objects.all().count()
    extract_article_count = models.ExtractArticle.objects.all().count()
    # transform counts
    transform_collection_count = models.TransformCollection.objects.all().count()
    transform_journal_count = models.TransformJournal.objects.all().count()
    transform_issue_count = models.TransformIssue.objects.all().count()
    transform_article_count = models.TransformArticle.objects.all().count()
    # load counts
    load_collection_count = models.LoadCollection.objects.all().count()
    load_journal_count = models.LoadJournal.objects.all().count()
    load_issue_count = models.LoadIssue.objects.all().count()
    load_article_count = models.LoadArticle.objects.all().count()
    # OPAC counts
    with switch_db(OpacCollection, OPAC_WEBAPP_DB_NAME):
        opac_collection_count = OpacCollection.objects.all().count()

    with switch_db(OpacJournal, OPAC_WEBAPP_DB_NAME):
        opac_journal_count = OpacJournal.objects.all().count()

    with switch_db(OpacIssue, OPAC_WEBAPP_DB_NAME):
        opac_issue_count = OpacIssue.objects.all().count()

    with switch_db(OpacArticle, OPAC_WEBAPP_DB_NAME):
        opac_article_count = OpacArticle.objects.all().count()

    with switch_db(OpacPressRelease, OPAC_WEBAPP_DB_NAME):
        opac_pressrelease_count = OpacPressRelease.objects.all().count()

    with switch_db(OpacSponsor, OPAC_WEBAPP_DB_NAME):
        opac_sponsor_count = OpacSponsor.objects.all().count()

    with switch_db(OpacPages, OPAC_WEBAPP_DB_NAME):
        opac_page_count = OpacPages.objects.all().count()

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
        'opac_pressrelease_count': opac_pressrelease_count,
        'opac_page_count': opac_page_count,
        'opac_news_count': opac_news_count,
    }
    return render_template("home.html", **context)
