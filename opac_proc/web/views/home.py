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
from opac_proc.datastore import identifiers_models
from opac_proc.datastore import diff_models


def home():
    register_connections()
    opac_webapp_db_name = get_opac_webapp_db_name()

    # identifiers:
    ids_collection_count = identifiers_models.CollectionIdModel.objects.all().count()
    ids_journal_count = identifiers_models.JournalIdModel.objects.all().count()
    ids_issue_count = identifiers_models.IssueIdModel.objects.all().count()
    ids_article_count = identifiers_models.ArticleIdModel.objects.all().count()
    ids_press_release_count = identifiers_models.PressReleaseIdModel.objects.all().count()
    ids_news_count = identifiers_models.NewsIdModel.objects.all().count()

    # extract counts
    extract_collection_count = models.ExtractCollection.objects.all().count()
    extract_journal_count = models.ExtractJournal.objects.all().count()
    extract_issue_count = models.ExtractIssue.objects.all().count()
    extract_article_count = models.ExtractArticle.objects.all().count()
    extract_press_release_count = models.ExtractPressRelease.objects.all().count()
    extract_news_count = models.ExtractNews.objects.all().count()

    # transform counts
    transform_collection_count = models.TransformCollection.objects.all().count()
    transform_journal_count = models.TransformJournal.objects.all().count()
    transform_issue_count = models.TransformIssue.objects.all().count()
    transform_article_count = models.TransformArticle.objects.all().count()
    transform_press_release_count = models.TransformPressRelease.objects.all().count()
    transform_news_count = models.TransformNews.objects.all().count()

    # load counts
    load_collection_count = models.LoadCollection.objects.all().count()
    load_journal_count = models.LoadJournal.objects.all().count()
    load_issue_count = models.LoadIssue.objects.all().count()
    load_article_count = models.LoadArticle.objects.all().count()
    load_press_release_count = models.LoadPressRelease.objects.all().count()
    load_news_count = models.LoadNews.objects.all().count()

    # OPAC counts
    with switch_db(OpacCollection, opac_webapp_db_name):
        opac_collection_count = OpacCollection.objects.all().count()

    with switch_db(OpacJournal, opac_webapp_db_name):
        opac_journal_count = OpacJournal.objects.all().count()

    with switch_db(OpacIssue, opac_webapp_db_name):
        opac_issue_count = OpacIssue.objects.all().count()

    with switch_db(OpacArticle, opac_webapp_db_name):
        opac_article_count = OpacArticle.objects.all().count()

    with switch_db(OpacPressRelease, opac_webapp_db_name):
        opac_pressrelease_count = OpacPressRelease.objects.all().count()

    with switch_db(OpacSponsor, opac_webapp_db_name):
        opac_sponsor_count = OpacSponsor.objects.all().count()

    with switch_db(OpacPages, opac_webapp_db_name):
        opac_page_count = OpacPages.objects.all().count()

    with switch_db(OpacNews, opac_webapp_db_name):
        opac_news_count = OpacNews.objects.all().count()

    # diff models - extract
    diff_ex_add_collection_count = diff_models.CollectionDiffModel.objects.filter(stage='extract', action='add', done_at=None).count()
    diff_ex_upd_collection_count = diff_models.CollectionDiffModel.objects.filter(stage='extract', action='update', done_at=None).count()
    diff_ex_del_collection_count = diff_models.CollectionDiffModel.objects.filter(stage='extract', action='delete', done_at=None).count()

    diff_ex_add_journal_count = diff_models.JournalDiffModel.objects.filter(stage='extract', action='add', done_at=None).count()
    diff_ex_upd_journal_count = diff_models.JournalDiffModel.objects.filter(stage='extract', action='update', done_at=None).count()
    diff_ex_del_journal_count = diff_models.JournalDiffModel.objects.filter(stage='extract', action='delete', done_at=None).count()

    diff_ex_add_issue_count = diff_models.IssueDiffModel.objects.filter(stage='extract', action='add', done_at=None).count()
    diff_ex_upd_issue_count = diff_models.IssueDiffModel.objects.filter(stage='extract', action='update', done_at=None).count()
    diff_ex_del_issue_count = diff_models.IssueDiffModel.objects.filter(stage='extract', action='delete', done_at=None).count()

    diff_ex_add_article_count = diff_models.ArticleDiffModel.objects.filter(stage='extract', action='add', done_at=None).count()
    diff_ex_upd_article_count = diff_models.ArticleDiffModel.objects.filter(stage='extract', action='update', done_at=None).count()
    diff_ex_del_article_count = diff_models.ArticleDiffModel.objects.filter(stage='extract', action='delete', done_at=None).count()

    diff_ex_add_press_release_count = diff_models.PressReleaseDiffModel.objects.filter(stage='extract', action='add', done_at=None).count()
    diff_ex_upd_press_release_count = diff_models.PressReleaseDiffModel.objects.filter(stage='extract', action='update', done_at=None).count()
    diff_ex_del_press_release_count = diff_models.PressReleaseDiffModel.objects.filter(stage='extract', action='delete', done_at=None).count()

    diff_ex_add_news_count = diff_models.NewsDiffModel.objects.filter(stage='extract', action='add', done_at=None).count()
    diff_ex_upd_news_count = diff_models.NewsDiffModel.objects.filter(stage='extract', action='update', done_at=None).count()
    diff_ex_del_news_count = diff_models.NewsDiffModel.objects.filter(stage='extract', action='delete', done_at=None).count()

    # diff models - transform
    diff_tr_add_collection_count = diff_models.CollectionDiffModel.objects.filter(stage='transform', action='add', done_at=None).count()
    diff_tr_upd_collection_count = diff_models.CollectionDiffModel.objects.filter(stage='transform', action='update', done_at=None).count()
    diff_tr_del_collection_count = diff_models.CollectionDiffModel.objects.filter(stage='transform', action='delete', done_at=None).count()

    diff_tr_add_journal_count = diff_models.JournalDiffModel.objects.filter(stage='transform', action='add', done_at=None).count()
    diff_tr_upd_journal_count = diff_models.JournalDiffModel.objects.filter(stage='transform', action='update', done_at=None).count()
    diff_tr_del_journal_count = diff_models.JournalDiffModel.objects.filter(stage='transform', action='delete', done_at=None).count()

    diff_tr_add_issue_count = diff_models.IssueDiffModel.objects.filter(stage='transform', action='add', done_at=None).count()
    diff_tr_upd_issue_count = diff_models.IssueDiffModel.objects.filter(stage='transform', action='update', done_at=None).count()
    diff_tr_del_issue_count = diff_models.IssueDiffModel.objects.filter(stage='transform', action='delete', done_at=None).count()

    diff_tr_add_article_count = diff_models.ArticleDiffModel.objects.filter(stage='transform', action='add', done_at=None).count()
    diff_tr_upd_article_count = diff_models.ArticleDiffModel.objects.filter(stage='transform', action='update', done_at=None).count()
    diff_tr_del_article_count = diff_models.ArticleDiffModel.objects.filter(stage='transform', action='delete', done_at=None).count()

    diff_tr_add_press_release_count = diff_models.PressReleaseDiffModel.objects.filter(stage='transform', action='add', done_at=None).count()
    diff_tr_upd_press_release_count = diff_models.PressReleaseDiffModel.objects.filter(stage='transform', action='update', done_at=None).count()
    diff_tr_del_press_release_count = diff_models.PressReleaseDiffModel.objects.filter(stage='transform', action='delete', done_at=None).count()

    diff_tr_add_news_count = diff_models.NewsDiffModel.objects.filter(stage='transform', action='add', done_at=None).count()
    diff_tr_upd_news_count = diff_models.NewsDiffModel.objects.filter(stage='transform', action='update', done_at=None).count()
    diff_tr_del_news_count = diff_models.NewsDiffModel.objects.filter(stage='transform', action='delete', done_at=None).count()

    # diff models - load
    diff_lo_add_collection_count = diff_models.CollectionDiffModel.objects.filter(stage='load', action='add', done_at=None).count()
    diff_lo_upd_collection_count = diff_models.CollectionDiffModel.objects.filter(stage='load', action='update', done_at=None).count()
    diff_lo_del_collection_count = diff_models.CollectionDiffModel.objects.filter(stage='load', action='delete', done_at=None).count()

    diff_lo_add_journal_count = diff_models.JournalDiffModel.objects.filter(stage='load', action='add', done_at=None).count()
    diff_lo_upd_journal_count = diff_models.JournalDiffModel.objects.filter(stage='load', action='update', done_at=None).count()
    diff_lo_del_journal_count = diff_models.JournalDiffModel.objects.filter(stage='load', action='delete', done_at=None).count()

    diff_lo_add_issue_count = diff_models.IssueDiffModel.objects.filter(stage='load', action='add', done_at=None).count()
    diff_lo_upd_issue_count = diff_models.IssueDiffModel.objects.filter(stage='load', action='update', done_at=None).count()
    diff_lo_del_issue_count = diff_models.IssueDiffModel.objects.filter(stage='load', action='delete', done_at=None).count()

    diff_lo_add_article_count = diff_models.ArticleDiffModel.objects.filter(stage='load', action='add', done_at=None).count()
    diff_lo_upd_article_count = diff_models.ArticleDiffModel.objects.filter(stage='load', action='update', done_at=None).count()
    diff_lo_del_article_count = diff_models.ArticleDiffModel.objects.filter(stage='load', action='delete', done_at=None).count()

    diff_lo_add_press_release_count = diff_models.PressReleaseDiffModel.objects.filter(stage='load', action='add', done_at=None).count()
    diff_lo_upd_press_release_count = diff_models.PressReleaseDiffModel.objects.filter(stage='load', action='update', done_at=None).count()
    diff_lo_del_press_release_count = diff_models.PressReleaseDiffModel.objects.filter(stage='load', action='delete', done_at=None).count()

    diff_lo_add_news_count = diff_models.NewsDiffModel.objects.filter(stage='load', action='add', done_at=None).count()
    diff_lo_upd_news_count = diff_models.NewsDiffModel.objects.filter(stage='load', action='update', done_at=None).count()
    diff_lo_del_news_count = diff_models.NewsDiffModel.objects.filter(stage='load', action='delete', done_at=None).count()

    latest_msg = models.Message.objects.filter(unread=True).order_by('-created_at')[:5]

    context = {
        # identifiers
        'ids_collection_count': ids_collection_count,
        'ids_journal_count': ids_journal_count,
        'ids_issue_count': ids_issue_count,
        'ids_article_count': ids_article_count,
        'ids_press_release_count': ids_press_release_count,
        'ids_news_count': ids_news_count,

        # extract
        'extract_collection_count': extract_collection_count,
        'extract_journal_count': extract_journal_count,
        'extract_issue_count': extract_issue_count,
        'extract_article_count': extract_article_count,
        'extract_press_release_count': extract_press_release_count,
        'extract_news_count': extract_news_count,

        # tranform
        'transform_collection_count': transform_collection_count,
        'transform_journal_count': transform_journal_count,
        'transform_issue_count': transform_issue_count,
        'transform_article_count': transform_article_count,
        'transform_press_release_count': transform_press_release_count,
        'transform_news_count': transform_news_count,

        # load
        'load_collection_count': load_collection_count,
        'load_journal_count': load_journal_count,
        'load_issue_count': load_issue_count,
        'load_article_count': load_article_count,
        'load_press_release_count': load_press_release_count,
        'load_news_count': load_news_count,

        # opac
        'opac_collection_count': opac_collection_count,
        'opac_journal_count': opac_journal_count,
        'opac_issue_count': opac_issue_count,
        'opac_article_count': opac_article_count,
        'opac_pressrelease_count': opac_pressrelease_count,
        'opac_news_count': opac_news_count,

        # opac outros modelos
        'opac_sponsor_count': opac_sponsor_count,
        'opac_page_count': opac_page_count,

        # diff ex:
        'diff_ex_add_collection_count': diff_ex_add_collection_count,
        'diff_ex_upd_collection_count': diff_ex_upd_collection_count,
        'diff_ex_del_collection_count': diff_ex_del_collection_count,
        'diff_ex_add_journal_count': diff_ex_add_journal_count,
        'diff_ex_upd_journal_count': diff_ex_upd_journal_count,
        'diff_ex_del_journal_count': diff_ex_del_journal_count,
        'diff_ex_add_issue_count': diff_ex_add_issue_count,
        'diff_ex_upd_issue_count': diff_ex_upd_issue_count,
        'diff_ex_del_issue_count': diff_ex_del_issue_count,
        'diff_ex_add_article_count': diff_ex_add_article_count,
        'diff_ex_upd_article_count': diff_ex_upd_article_count,
        'diff_ex_del_article_count': diff_ex_del_article_count,
        'diff_ex_add_press_release_count': diff_ex_add_press_release_count,
        'diff_ex_upd_press_release_count': diff_ex_upd_press_release_count,
        'diff_ex_del_press_release_count': diff_ex_del_press_release_count,
        'diff_ex_add_news_count': diff_ex_add_news_count,
        'diff_ex_upd_news_count': diff_ex_upd_news_count,
        'diff_ex_del_news_count': diff_ex_del_news_count,
        # diff tr:
        'diff_tr_add_collection_count': diff_tr_add_collection_count,
        'diff_tr_upd_collection_count': diff_tr_upd_collection_count,
        'diff_tr_del_collection_count': diff_tr_del_collection_count,
        'diff_tr_add_journal_count': diff_tr_add_journal_count,
        'diff_tr_upd_journal_count': diff_tr_upd_journal_count,
        'diff_tr_del_journal_count': diff_tr_del_journal_count,
        'diff_tr_add_issue_count': diff_tr_add_issue_count,
        'diff_tr_upd_issue_count': diff_tr_upd_issue_count,
        'diff_tr_del_issue_count': diff_tr_del_issue_count,
        'diff_tr_add_article_count': diff_tr_add_article_count,
        'diff_tr_upd_article_count': diff_tr_upd_article_count,
        'diff_tr_del_article_count': diff_tr_del_article_count,
        'diff_tr_add_press_release_count': diff_tr_add_press_release_count,
        'diff_tr_upd_press_release_count': diff_tr_upd_press_release_count,
        'diff_tr_del_press_release_count': diff_tr_del_press_release_count,
        'diff_tr_add_news_count': diff_tr_add_news_count,
        'diff_tr_upd_news_count': diff_tr_upd_news_count,
        'diff_tr_del_news_count': diff_tr_del_news_count,
        # diff lo:
        'diff_lo_add_collection_count': diff_lo_add_collection_count,
        'diff_lo_upd_collection_count': diff_lo_upd_collection_count,
        'diff_lo_del_collection_count': diff_lo_del_collection_count,
        'diff_lo_add_journal_count': diff_lo_add_journal_count,
        'diff_lo_upd_journal_count': diff_lo_upd_journal_count,
        'diff_lo_del_journal_count': diff_lo_del_journal_count,
        'diff_lo_add_issue_count': diff_lo_add_issue_count,
        'diff_lo_upd_issue_count': diff_lo_upd_issue_count,
        'diff_lo_del_issue_count': diff_lo_del_issue_count,
        'diff_lo_add_article_count': diff_lo_add_article_count,
        'diff_lo_upd_article_count': diff_lo_upd_article_count,
        'diff_lo_del_article_count': diff_lo_del_article_count,
        'diff_lo_add_press_release_count': diff_lo_add_press_release_count,
        'diff_lo_upd_press_release_count': diff_lo_upd_press_release_count,
        'diff_lo_del_press_release_count': diff_lo_del_press_release_count,
        'diff_lo_add_news_count': diff_lo_add_news_count,
        'diff_lo_upd_news_count': diff_lo_upd_news_count,
        'diff_lo_del_news_count': diff_lo_del_news_count,

        'latest_msg': latest_msg
    }
    return render_template("home.html", **context)
