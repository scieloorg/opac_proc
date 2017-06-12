# coding: utf-8
from opac_proc.transformers.tr_collections import CollectionTransformer
from opac_proc.transformers.tr_journals import JournalTransformer
from opac_proc.transformers.tr_issues import IssueTransformer
from opac_proc.transformers.tr_articles import ArticleTransformer
from opac_proc.transformers.tr_press_releases import PressReleaseTransformer
from opac_proc.transformers.tr_news import NewsTransformer
from opac_proc.datastore import models
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "transform")
else:
    logger = getMongoLogger(__name__, "INFO", "transform")
# Collections:


def task_transform_collection():
    acronym = config.OPAC_PROC_COLLECTION
    transformer = CollectionTransformer(extract_model_key=acronym)
    transformer.transform()
    transformer.save()


def task_collection_update(ids=None):
    get_db_connection()
    stage = 'transform'
    model = 'collection'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    if ids is None:  # update all collections
        models.TransformCollection.objects.all().update(must_reprocess=True)
        for collection in models.TransformCollection.objects.all():
            r_queues.enqueue(
                stage, model,
                task_transform_collection)
    else:
        for oid in ids:
            try:
                obj = models.TransformCollection.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(
                    stage, 'collection',
                    task_transform_collection)
            except Exception as e:
                logger.error('models.TransformCollection %s. pk: %s', str(e), oid)


def task_collection_create():
    get_db_connection()
    stage = 'transform'
    model = 'collection'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)
    r_queues.enqueue(
        stage, model,
        task_transform_collection)


# Journals:


def task_transform_journal(acronym, issn):
    transformer = JournalTransformer(extract_model_key=issn)
    transformer.transform()
    transformer.save()


def task_journal_update(ids=None):
    get_db_connection()
    stage = 'transform'
    model = 'journal'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)
    collection = models.TransformCollection.objects.all().first()
    if ids is None:  # update all collections
        models.TransformJournal.objects.all().update(must_reprocess=True)
        for journal in models.TransformJournal.objects.all():
            issn = journal.get('scielo_issn', False) or \
                   journal.get('print_issn', False) or \
                   journal.get('eletronic_issn', False)
            if not issn:
                raise ValueError(u'Journal sem issn')
            r_queues.enqueue(
                stage, model,
                task_transform_journal, collection.acronym, issn)
    else:
        for oid in ids:
            try:
                obj = models.TransformJournal.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                issn = obj.get('scielo_issn', False) or \
                    obj.get('print_issn', False) or \
                    obj.get('eletronic_issn', False)
                if not issn:
                    raise ValueError(u'Journal sem issn')
                r_queues.enqueue(
                    stage, model,
                    task_transform_journal, collection.acronym, issn)
            except Exception as e:
                logger.error('models.TransformJournal %s. pk: %s', str(e), oid)


def task_journal_create():
    get_db_connection()
    stage = 'transform'
    model = 'journal'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    collection = models.TransformCollection.objects.all().first()

    for child in collection.children_ids:
        r_queues.enqueue(
            stage, model,
            task_transform_journal, collection.acronym, child['issn'])


# Issues:


def task_transform_issue(acronym, issue_id):
    transformer = IssueTransformer(extract_model_key=issue_id)
    transformer.transform()
    transformer.save()


def task_issue_update(ids=None):
    get_db_connection()
    stage = 'transform'
    model = 'issue'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)
    collection = models.TransformCollection.objects.all().first()

    if ids is None:  # update all collections
        models.TransformIssue.objects.all().update(must_reprocess=True)
        for issue in models.TransformIssue.objects.all():
            r_queues.enqueue(
                stage, model,
                task_transform_issue, collection.acronym, issue.pid)
    else:
        for oid in ids:
            try:
                obj = models.TransformIssue.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(
                    stage, model,
                    task_transform_issue, collection.acronym, obj.pid)
            except Exception as e:
                logger.error('models.TransformIssue %s. pk: %s', str(e), oid)


def task_issue_create():
    get_db_connection()
    stage = 'transform'
    model = 'issue'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    collection = models.TransformCollection.objects.all().first()

    for child in collection.children_ids:
        issues_ids = child['issues_ids']
        for issue_pid in issues_ids:
            r_queues.enqueue(
                stage, model,
                task_transform_issue, collection.acronym, issue_pid)


# Articles:


def task_transform_article(acronym, article_id):
    transformer = ArticleTransformer(extract_model_key=article_id)
    transformer.transform()
    transformer.save()


def task_article_update(ids=None):
    get_db_connection()
    stage = 'transform'
    model = 'article'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    collection = models.TransformCollection.objects.all().first()

    if ids is None:  # update all collections
        models.TransformArticle.objects.all().update(must_reprocess=True)
        for article in models.TransformArticle.objects.all():
            r_queues.enqueue(
                stage, model,
                task_transform_article, collection.acronym, article.pid)
    else:
        for oid in ids:
            try:
                obj = models.TransformArticle.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(
                    stage, model,
                    task_transform_article, collection.acronym, obj.pid)
            except Exception as e:
                logger.error('models.TransformArticle %s. pk: %s', str(e), oid)


def task_article_create():
    get_db_connection()
    stage = 'transform'
    model = 'article'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    collection = models.TransformCollection.objects.all().first()

    for child in collection.children_ids:
        articles_ids = child['articles_ids']
        for article_pid in articles_ids:
            r_queues.enqueue(
                stage, model,
                task_transform_article, collection.acronym, article_pid)


# Press releases


def task_transform_press_release(press_release_uuid):
    transformer = PressReleaseTransformer(extract_model_key=press_release_uuid)
    transformer.transform()
    transformer.save()


def task_press_release_update(ids=None):
    get_db_connection()
    stage = 'transform'
    model = 'press_release'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    if ids is None:  # update all Press Releases
        models.TransformPressRelease.objects.all().update(must_reprocess=True)
        for pr in models.TransformPressRelease.objects.all():
            r_queues.enqueue(
                stage, model,
                task_transform_press_release, press_release_uuid=pr.uuid)
    else:
        for oid in ids:
            try:
                obj = models.TransformPressRelease.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(
                    stage, model,
                    task_transform_press_release, press_release_uuid=obj.uuid)
            except Exception as e:
                logger.error('models.TransformPressRelease %s. pk: %s', str(e), oid)


def task_press_release_create():
    get_db_connection()
    stage = 'transform'
    model = 'press_release'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    for pr in models.ExtractPressRelease.objects.all():
        r_queues.enqueue(
            stage, model,
            task_transform_press_release, press_release_uuid=pr.uuid)


# News


def task_transform_news(news_uuid):
    transformer = NewsTransformer(extract_model_key=news_uuid)
    transformer.transform()
    transformer.save()


def task_news_update(ids=None):
    get_db_connection()
    stage = 'transform'
    model = 'news'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    if ids is None:  # update all News
        models.TransformNews.objects.all().update(must_reprocess=True)
        for news in models.TransformNews.objects.all():
            r_queues.enqueue(
                stage, model,
                task_transform_news, news_uuid=news.uuid)
    else:
        for oid in ids:
            try:
                obj = models.TransformNews.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(
                    stage, model,
                    task_transform_news, news_uuid=obj.uuid)
            except Exception as e:
                logger.error('models.TransformNews %s. pk: %s', str(e), oid)


def task_news_create():
    get_db_connection()
    stage = 'transform'
    model = 'news'
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    for news in models.ExtractNews.objects.all():
        r_queues.enqueue(
            stage, model,
            task_transform_news, news_uuid=news.uuid)
