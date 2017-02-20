# coding: utf-8
from opac_proc.transformers.tr_collections import CollectionTransformer
from opac_proc.transformers.tr_journals import JournalTransformer
from opac_proc.transformers.tr_issues import IssueTransformer
from opac_proc.transformers.tr_articles import ArticleTransformer
from opac_proc.datastore import models
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.transformers.tr_press_releases import PressReleaseTransformer
from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "transform")
else:
    logger = getMongoLogger(__name__, "INFO", "transform")


# --------------------------------------------------- #
#               COLLECTIONS                           #
# --------------------------------------------------- #S
def task_transform_collection(acronym):
    transformer = CollectionTransformer(extract_model_key=acronym)
    transformer.transform()
    transformer.save()


def task_reprocess_collections(ids=None):
    get_db_connection()
    stage = "transform"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    if ids is None:  # update all collections
        models.TransformCollection.objects.all().update(must_reprocess=True)
        for collection in models.TransformCollection.objects.all():
            r_queues.enqueue(stage, 'collection', task_transform_collection, collection.acronym)
    else:
        for oid in ids:
            try:
                obj = models.TransformCollection.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(stage, 'collection', task_transform_collection, obj.acronym)
            except Exception as e:
                logger.error('models.TransformCollection %s. pk: %s' % (str(e), oid))


def task_process_all_collections(acronym):
    get_db_connection()
    stage = "transform"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)
    r_queues.enqueue(stage, 'collection', task_transform_collection, acronym)


# --------------------------------------------------- #
#               JOURNALS                              #
# --------------------------------------------------- #
def task_transform_journal(acronym, issn):
    transformer = JournalTransformer(extract_model_key=issn)
    transformer.transform()
    transformer.save()


def task_reprocess_journals(ids=None):
    get_db_connection()
    stage = "transform"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)
    collection = models.TransformCollection.objects.all().first()
    if ids is None:  # update all collections
        models.TransformJournal.objects.all().update(must_reprocess=True)
        for journal in models.TransformJournal.objects.all():
            issn = journal.get('scielo_issn', False) or journal.get('print_issn', False) or journal.get(
                'eletronic_issn', False)
            if not issn:
                raise ValueError(u'Journal sem issn')
            r_queues.enqueue(stage, 'journal', task_transform_journal, collection.acronym, issn)
    else:
        for oid in ids:
            try:
                obj = models.TransformJournal.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                issn = obj.get('scielo_issn', False) or obj.get('print_issn', False) or obj.get('eletronic_issn', False)
                if not issn:
                    raise ValueError(u'Journal sem issn')
                r_queues.enqueue(stage, 'journal', task_transform_journal, collection.acronym, issn)
            except Exception as e:
                logger.error('models.TransformJournal %s. pk: %s' % (str(e), oid))


def task_process_all_journals():
    get_db_connection()
    stage = "transform"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    collection = models.TransformCollection.objects.all().first()

    for child in collection.children_ids:
        r_queues.enqueue(stage, 'collection', task_transform_journal, collection.acronym, child['issn'])


# --------------------------------------------------- #
#               ISSUES                                #
# --------------------------------------------------- #
def task_transform_issue(acronym, issue_id):
    transformer = IssueTransformer(extract_model_key=issue_id)
    transformer.transform()
    transformer.save()


def task_reprocess_issues(ids=None):
    get_db_connection()
    stage = "transform"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    if ids is None:  # update all collections
        models.TransformIssue.objects.all().update(must_reprocess=True)
        for issue in models.TransformIssue.objects.all():
            r_queues.enqueue(stage, 'issue', task_transform_issue, issue.code)
    else:
        for oid in ids:
            try:
                obj = models.TransformIssue.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(stage, 'issue', task_transform_issue, obj.code)
            except Exception as e:
                logger.error('models.TransformIssue %s. pk: %s' % (str(e), oid))


def task_process_all_issues():
    get_db_connection()
    stage = "transform"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    collection = models.TransformCollection.objects.all().first()

    for child in collection.children_ids:
        issues_ids = child['issues_ids']
        for issue_pid in issues_ids:
            r_queues.enqueue(stage, 'issue', task_transform_issue, collection.acronym, issue_pid)


# --------------------------------------------------- #
#               ARTICLES                              #
# --------------------------------------------------- #
def task_transform_article(article_id):
    transformer = ArticleTransformer(extract_model_key=article_id)
    transformer.transform()
    transformer.save()


def task_reprocess_articles(ids=None):
    get_db_connection()
    stage = "transform"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    collection = models.TransformCollection.objects.all().first()

    if ids is None:  # update all collections
        models.TransformArticle.objects.all().update(must_reprocess=True)
        for article in models.TransformArticle.objects.all():
            r_queues.enqueue(stage, 'article', task_transform_article, collection.acronym, article.pid)
    else:
        for oid in ids:
            try:
                obj = models.TransformArticle.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(stage, 'article', task_transform_article, collection.acronym, obj.pid)
            except Exception as e:
                logger.error('models.TransformArticle %s. pk: %s' % (str(e), oid))


def task_process_all_articles():
    get_db_connection()
    stage = "transform"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    collection = models.TransformCollection.objects.all().first()

    for child in collection.children_ids:
        articles_ids = child['articles_ids']
        for article_pid in articles_ids:
            r_queues.enqueue(stage, 'article', task_transform_article, article_pid)


# --------------------------------------------------- #
#               PRESS RELEASES                        #
# --------------------------------------------------- #
def task_transform_press_release(press_release_id):
    transformer = PressReleaseTransformer(extract_model_key=press_release_id)
    transformer.transform()
    transformer.save()


def task_process_all_press_releases():
    get_db_connection()
    stage = "transform"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    press_releases = models.ExtractPressRelease.objects.all()

    for press_release in press_releases:
        r_queues.enqueue(stage, 'press_release', task_transform_press_release, press_release._id)
