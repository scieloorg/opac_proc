# coding: utf-8

from opac_proc.loaders.lo_collections import CollectionLoader
from opac_proc.loaders.lo_journals import JournalLoader
from opac_proc.loaders.lo_issues import IssueLoader
from opac_proc.loaders.lo_articles import ArticleLoader
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


def task_reprocess_collections(ids=None):
    get_db_connection()
    stage = "load"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    if ids is None:  # update all collections
        models.LoadCollection.objects.all().update(must_reprocess=True)
        for collection in models.LoadCollection.objects.all():
            r_queues.enqueue(stage, 'collection', task_load_collection, collection.uuid)
    else:
        for oid in ids:
            try:
                obj = models.LoadCollection.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(stage, 'collection', task_load_collection, obj.uuid)
            except Exception as e:
                logger.error('models.LoadCollection %s. pk: %s' % (str(e), oid))


def task_process_all_collections():
    get_db_connection()
    stage = "load"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    for collection in models.TransformCollection.objects.all():
        r_queues.enqueue(stage, 'collection', task_load_collection, collection.uuid)

# Journals:


def task_load_journal(uuid):
    j_loader = JournalLoader(uuid)
    j_loader.prepare()
    j_loader.load()


def task_reprocess_journals(ids=None):
    get_db_connection()
    stage = "load"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    if ids is None:  # update all collections
        models.LoadJournal.objects.all().update(must_reprocess=True)
        for journal in models.LoadJournal.objects.all():
            r_queues.enqueue(stage, 'journal', task_load_journal, journal.uuid)
    else:
        for oid in ids:
            try:
                obj = models.LoadJournal.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(stage, 'journal', task_load_journal, obj.uuid)
            except Exception as e:
                logger.error('models.LoadJournal %s. pk: %s' % (str(e), oid))


def task_process_all_journals():
    get_db_connection()
    stage = "load"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    for journal in models.TransformJournal.objects.all():
        r_queues.enqueue(stage, 'collection', task_load_journal, journal.uuid)


# Issues:


def task_load_issue(uuid):
    i_loader = IssueLoader(uuid)
    i_loader.prepare()
    i_loader.load()


def task_reprocess_issues(ids=None):
    get_db_connection()
    stage = "load"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    if ids is None:  # update all collections
        models.LoadIssue.objects.all().update(must_reprocess=True)
        for issue in models.LoadIssue.objects.all():
            r_queues.enqueue(stage, 'issue', task_load_issue, issue.uuid)
    else:
        for oid in ids:
            try:
                obj = models.LoadIssue.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(stage, 'issue', task_load_issue, obj.uuid)
            except Exception as e:
                logger.error('models.LoadIssue %s. pk: %s' % (str(e), oid))


def task_process_all_issues():
    get_db_connection()
    stage = "load"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    for issue in models.TransformIssue.objects.all():
        r_queues.enqueue(stage, 'issue', task_load_issue, issue.uuid)


# Articles:


def task_load_article(uuid):
    a_loader = ArticleLoader(uuid)
    a_loader.prepare()
    a_loader.load()


def task_reprocess_articles(ids=None):
    get_db_connection()
    stage = "load"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    if ids is None:  # update all collections
        models.LoadArticle.objects.all().update(must_reprocess=True)
        for article in models.LoadArticle.objects.all():
            r_queues.enqueue(stage, 'article', task_load_article, article.uuid)
    else:
        for oid in ids:
            try:
                obj = models.LoadArticle.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(stage, 'article', task_load_article, obj.uuid)
            except Exception as e:
                logger.error('models.LoadArticle %s. pk: %s' % (str(e), oid))


def task_process_all_articles():
    get_db_connection()
    stage = "load"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    for article in models.TransformArticle.objects.all():
        r_queues.enqueue(stage, 'article', task_load_article, article.uuid)
