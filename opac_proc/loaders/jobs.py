# coding: utf-8

from opac_proc.loaders.lo_collections import CollectionLoader
from opac_proc.loaders.lo_journals import JournalLoader
from opac_proc.loaders.lo_issues import IssueLoader
from opac_proc.loaders.lo_articles import ArticleLoader
from opac_proc.loaders.lo_press_releases import PressReleaseLoader
from opac_proc.loaders.lo_news import NewsLoader
from opac_proc.datastore import models
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "load")
else:
    logger = getMongoLogger(__name__, "INFO", "load")


# Collections:


def task_load_collection(uuid):
    c_loader = CollectionLoader(uuid)
    c_loader.prepare()
    c_loader.load()


def task_collection_update(ids=None):
    get_db_connection()
    stage = 'load'
    model = 'collection'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    if ids is None:  # update all collections
        models.LoadCollection.objects.all().update(must_reprocess=True)
        for collection in models.LoadCollection.objects.all():
            r_queues.enqueue(stage, model, task_load_collection, collection.uuid)
    else:
        for oid in ids:
            try:
                obj = models.LoadCollection.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(stage, model, task_load_collection, obj.uuid)
            except Exception as e:
                logger.error('models.LoadCollection %s. pk: %s' % (str(e), oid))


def task_collection_create():
    get_db_connection()
    stage = 'load'
    model = 'collection'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    for collection in models.TransformCollection.objects.all():
        r_queues.enqueue(stage, model, task_load_collection, collection.uuid)

# Journals:


def task_load_journal(uuid):
    j_loader = JournalLoader(uuid)
    j_loader.prepare()
    j_loader.load()


def task_journal_update(ids=None):
    get_db_connection()
    stage = 'load'
    model = 'journal'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    if ids is None:  # update all collections
        models.LoadJournal.objects.all().update(must_reprocess=True)
        for journal in models.LoadJournal.objects.all():
            r_queues.enqueue(stage, model, task_load_journal, journal.uuid)
    else:
        for oid in ids:
            try:
                obj = models.LoadJournal.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(stage, model, task_load_journal, obj.uuid)
            except Exception as e:
                logger.error('models.LoadJournal %s. pk: %s' % (str(e), oid))


def task_journal_create():
    get_db_connection()
    stage = 'load'
    model = 'journal'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    for journal in models.TransformJournal.objects.all():
        r_queues.enqueue(
            stage, model,
            task_load_journal, uuid=journal.uuid)


# Issues:


def task_load_issue(uuid):
    i_loader = IssueLoader(uuid)
    i_loader.prepare()
    i_loader.load()


def task_issue_create(ids=None):
    get_db_connection()
    stage = 'load'
    model = 'issue'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    if ids is None:  # update all collections
        models.LoadIssue.objects.all().update(must_reprocess=True)
        for issue in models.LoadIssue.objects.all():
            r_queues.enqueue(
                stage, model,
                task_load_issue, uuid=issue.uuid)
    else:
        for oid in ids:
            try:
                obj = models.LoadIssue.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(
                    stage, model,
                    task_load_issue, uuid=obj.uuid)
            except Exception as e:
                logger.error('models.LoadIssue %s. pk: %s' % (str(e), oid))


def task_issue_update():
    get_db_connection()
    stage = 'load'
    model = 'issue'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    for issue in models.TransformIssue.objects.all():
        r_queues.enqueue(
            stage, model,
            task_load_issue, uuid=issue.uuid)


# Articles:


def task_load_article(uuid):
    a_loader = ArticleLoader(uuid)
    a_loader.prepare()
    a_loader.load()


def task_article_update(ids=None):
    get_db_connection()
    stage = 'load'
    model = 'article'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    if ids is None:  # update all collections
        models.LoadArticle.objects.all().update(must_reprocess=True)
        for article in models.LoadArticle.objects.all():
            r_queues.enqueue(
                stage, model,
                task_load_article, uuid=article.uuid)
    else:
        for oid in ids:
            try:
                obj = models.LoadArticle.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(
                    stage, model,
                    task_load_article, uuid=obj.uuid)
            except Exception as e:
                logger.error('models.LoadArticle %s. pk: %s', str(e), oid)


def task_article_create():
    get_db_connection()
    stage = 'load'
    model = 'article'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    for article in models.TransformArticle.objects.all():
        r_queues.enqueue(
            stage, model,
            task_load_article, uuid=article.uuid)


# Press Release:


def task_load_press_release(uuid):
    pr_loader = PressReleaseLoader(uuid)
    pr_loader.prepare()
    pr_loader.load()


def task_press_release_update(ids=None):
    get_db_connection()
    stage = 'load'
    model = 'press_release'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    if ids is None:  # update all Press Releases
        models.LoadPressRelease.objects.all().update(must_reprocess=True)
        for pr in models.LoadPressRelease.objects.all():
            r_queues.enqueue(
                stage, model,
                task_load_press_release, uuid=pr.uuid)
    else:
        for oid in ids:
            try:
                obj = models.LoadPressRelease.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(
                    stage, model,
                    task_load_press_release, uuid=obj.uuid)
            except Exception as e:
                logger.error('models.LoadPressRelease %s. pk: %s', str(e), oid)


def task_press_release_create():
    get_db_connection()
    stage = 'load'
    model = 'press_release'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    for press_release in models.TransformPressRelease.objects.all():
        r_queues.enqueue(
            stage, model,
            task_load_press_release, uuid=press_release.uuid)


# News:


def task_load_news(uuid):
    news_loader = NewsLoader(uuid)
    news_loader.prepare()
    news_loader.load()


def task_news_update(ids=None):
    get_db_connection()
    stage = 'load'
    model = 'news'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    if ids is None:  # update all Press Releases
        models.LoadNews.objects.all().update(must_reprocess=True)
        for news in models.LoadNews.objects.all():
            r_queues.enqueue(
                stage, model,
                task_load_news, uuid=news.uuid)
    else:
        for oid in ids:
            try:
                obj = models.LoadNews.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(
                    stage, model,
                    task_load_news, uuid=obj.uuid)
            except Exception as e:
                logger.error('models.LoadNews %s. pk: %s', str(e), oid)


def task_news_create():
    get_db_connection()
    stage = 'load'
    model = 'news'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    for news in models.TransformNews.objects.all():
        r_queues.enqueue(
            stage, model,
            task_load_news, uuid=news.uuid)
