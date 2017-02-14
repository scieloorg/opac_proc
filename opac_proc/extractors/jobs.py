# coding: utf-8
from opac_proc.extractors.ex_collections import CollectionExtractor
from opac_proc.extractors.ex_journals import JournalExtractor
from opac_proc.extractors.ex_issues import IssueExtractor
from opac_proc.extractors.ex_articles import ArticleExtractor
from opac_proc.extractors.ex_press_releases import PressReleaseExtractor

from opac_proc.datastore import models
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import get_db_connection

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "extract")
else:
    logger = getMongoLogger(__name__, "INFO", "extract")


# --------------------------------------------------- #
#                   COLLECTION                        #
# --------------------------------------------------- #

def task_extract_collection(acronym):
    extractor = CollectionExtractor(acronym)
    extractor.extract()
    extractor.save()


def task_reprocess_collections(ids=None):
    get_db_connection()
    stage = "extract"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    if ids is None:  # update all collections
        models.ExtractCollection.objects.all().update(must_reprocess=True)
        for collection in models.ExtractCollection.objects.all():
            r_queues.enqueue(stage, 'collection', task_extract_collection, collection.acronym)
    else:
        for oid in ids:
            try:
                obj = models.ExtractCollection.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(stage, 'collection', task_extract_collection, obj.acronym)
            except Exception as e:
                logger.error('models.ExtractCollection %s. pk: %s' % (str(e), oid))


def task_process_all_collections(acronym):
    get_db_connection()
    stage = "extract"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)
    r_queues.enqueue(stage, 'collection', task_extract_collection, acronym)

# --------------------------------------------------- #
#                   JOURNALS                          #
# --------------------------------------------------- #

def task_extract_journal(acronym, issn):
    extractor = JournalExtractor(acronym, issn)
    extractor.extract()
    extractor.save()


def task_reprocess_journals(ids=None):
    get_db_connection()
    stage = "extract"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)
    collection = models.ExtractCollection.objects.all().first()
    if ids is None:  # update all collections
        models.ExtractJournal.objects.all().update(must_reprocess=True)
        for journal in models.ExtractJournal.objects.all():
            r_queues.enqueue(stage, 'journal', task_extract_journal, collection.acronym, journal.code)
    else:
        for oid in ids:
            try:
                obj = models.ExtractJournal.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(stage, 'journal', task_extract_journal, collection.acronym, obj.code)
            except Exception as e:
                logger.error('models.ExtractJournal %s. pk: %s' % (str(e), oid))


def task_process_all_journals():
    get_db_connection()
    stage = "extract"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    collection = models.ExtractCollection.objects.all().first()

    for child in collection.children_ids:
        r_queues.enqueue(stage, 'journal', task_extract_journal, collection.acronym, child['issn'])


# --------------------------------------------------- #
#                   ISSUES                            #
# --------------------------------------------------- #

def task_extract_issue(acronym, issue_id):
    extractor = IssueExtractor(acronym, issue_id)
    extractor.extract()
    extractor.save()


def task_reprocess_issues(ids=None):
    get_db_connection()
    stage = "extract"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    if ids is None:  # update all collections
        models.ExtractIssue.objects.all().update(must_reprocess=True)
        for issue in models.ExtractIssue.objects.all():
            r_queues.enqueue(stage, 'issue', task_extract_issue, issue.code)
    else:
        for oid in ids:
            try:
                obj = models.ExtractIssue.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(stage, 'issue', task_extract_issue, obj.code)
            except Exception as e:
                logger.error('models.ExtractIssue %s. pk: %s' % (str(e), oid))


def task_process_all_issues():
    get_db_connection()
    stage = "extract"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    collection = models.ExtractCollection.objects.all().first()

    for child in collection.children_ids:
        issues_ids = child['issues_ids']
        for issue_pid in issues_ids:
            r_queues.enqueue(stage, 'issue', task_extract_issue, collection.acronym, issue_pid)


# --------------------------------------------------- #
#                   ARTICLE                           #
# --------------------------------------------------- #


def task_extract_article(acronym, article_id):
    extractor = ArticleExtractor(acronym, article_id)
    extractor.extract()
    extractor.save()


def task_reprocess_articles(ids=None):
    get_db_connection()
    stage = "extract"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    if ids is None:  # update all collections
        models.ExtractArticle.objects.all().update(must_reprocess=True)
        for article in models.ExtractArticle.objects.all():
            r_queues.enqueue(stage, 'article', task_extract_article, article.code)
    else:
        for oid in ids:
            try:
                obj = models.ExtractArticle.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(stage, 'article', task_extract_article, obj.code)
            except Exception as e:
                logger.error('models.ExtractArticle %s. pk: %s' % (str(e), oid))


def task_process_all_articles():
    get_db_connection()
    stage = "extract"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    collection = models.ExtractCollection.objects.all().first()

    for child in collection.children_ids:
        articles_ids = child['articles_ids']
        for article_pid in articles_ids:
            r_queues.enqueue(stage, 'article', task_extract_article, collection.acronym, article_pid)


# --------------------------------------------------- #
#               PRESS RELEASES                        #
# --------------------------------------------------- #

def task_process_all_press_releases():
    get_db_connection()
    stage = "extract"
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    journal = models.ExtractJournal.objects.all()

    for child in journal.children_ids:
        articles_ids = child['articles_ids']
        for article_pid in articles_ids:
            r_queues.enqueue(stage, 'article', task_extract_article, child.acronym, article_pid)
