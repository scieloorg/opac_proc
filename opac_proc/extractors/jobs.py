# coding: utf-8
from flask import json

from opac_proc.extractors.ex_collections import CollectionExtractor
from opac_proc.extractors.ex_journals import JournalExtractor
from opac_proc.extractors.ex_issues import IssueExtractor
from opac_proc.extractors.ex_articles import ArticleExtractor
from opac_proc.extractors.ex_press_releases import PressReleaseExtractor
from opac_proc.extractors.ex_news import NewsExtractor
from xylose.scielodocument import Journal as xylose_journal

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

def task_extract_collection():
    acronym = config.OPAC_PROC_COLLECTION
    extractor = CollectionExtractor(acronym)
    extractor.extract()
    extractor.save()


def task_collection_update(ids=None):
    get_db_connection()
    stage = 'extract'
    model = 'collection'
    r_queues = RQueues()

    if ids is None:  # update all collections
        models.ExtractCollection.objects.all().update(must_reprocess=True)
        for collection in models.ExtractCollection.objects.all():
            r_queues.enqueue(stage, model, task_extract_collection)
    else:
        for oid in ids:
            try:
                obj = models.ExtractCollection.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(stage, model, task_extract_collection)
            except Exception as e:
                logger.error('models.ExtractCollection %s. pk: %s' % (str(e), oid))


def task_collection_create():
    get_db_connection()
    stage = 'extract'
    model = 'collection'
    r_queues = RQueues()
    r_queues.enqueue(stage, model, task_extract_collection)


# --------------------------------------------------- #
#                   JOURNALS                          #
# --------------------------------------------------- #

def task_extract_journal(acronym, issn):
    extractor = JournalExtractor(acronym, issn)
    extractor.extract()
    extractor.save()


def task_journal_update(ids=None):
    get_db_connection()
    stage = 'extract'
    model = 'journal'
    r_queues = RQueues()
    collection = models.ExtractCollection.objects.all().first()
    if ids is None:  # update all collections
        models.ExtractJournal.objects.all().update(must_reprocess=True)
        for journal in models.ExtractJournal.objects.all():
            r_queues.enqueue(stage, model, task_extract_journal, collection.acronym, journal.code)
    else:
        for oid in ids:
            try:
                obj = models.ExtractJournal.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(stage, model, task_extract_journal, collection.acronym, obj.code)
            except Exception as e:
                logger.error('models.ExtractJournal %s. pk: %s' % (str(e), oid))


def task_journal_create():
    get_db_connection()
    stage = 'extract'
    model = 'journal'
    r_queues = RQueues()

    collection = models.ExtractCollection.objects.all().first()

    for child in collection.children_ids:
        r_queues.enqueue(stage, model, task_extract_journal, collection.acronym, child['issn'])


# --------------------------------------------------- #
#                   ISSUES                            #
# --------------------------------------------------- #

def task_extract_issue(acronym, issue_id):
    extractor = IssueExtractor(acronym, issue_id)
    extractor.extract()
    extractor.save()


def task_issue_update(ids=None):
    get_db_connection()
    stage = 'extract'
    model = 'issue'
    r_queues = RQueues()

    collection = models.ExtractCollection.objects.all().first()

    if ids is None:  # update all collections
        models.ExtractIssue.objects.all().update(must_reprocess=True)
        for issue in models.ExtractIssue.objects.all():
            r_queues.enqueue(stage, model, task_extract_issue, collection.acronym, issue.code)
    else:
        for oid in ids:
            try:
                obj = models.ExtractIssue.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(stage, model, task_extract_issue, collection.acronym, obj.code)
            except Exception as e:
                logger.error('models.ExtractIssue %s. pk: %s' % (str(e), oid))


def task_issue_create():
    get_db_connection()
    stage = 'extract'
    model = 'issue'
    r_queues = RQueues()

    collection = models.ExtractCollection.objects.all().first()

    for child in collection.children_ids:
        issues_ids = child['issues_ids']
        for issue_pid in issues_ids:
            r_queues.enqueue(stage, model, task_extract_issue, collection.acronym, issue_pid)


# --------------------------------------------------- #
#                   ARTICLE                           #
# --------------------------------------------------- #


def task_extract_article(acronym, article_id):
    extractor = ArticleExtractor(acronym, article_id)
    extractor.extract()
    extractor.save()


def task_article_update(ids=None):
    get_db_connection()
    stage = 'extract'
    model = 'article'
    r_queues = RQueues()

    collection = models.ExtractCollection.objects.all().first()

    if ids is None:  # update all collections
        models.ExtractArticle.objects.all().update(must_reprocess=True)
        for article in models.ExtractArticle.objects.all():
            r_queues.enqueue(stage, model, task_extract_article, collection.acronym, article.code)
    else:
        for oid in ids:
            try:
                obj = models.ExtractArticle.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(stage, model, task_extract_article, collection.acronym, obj.code)
            except Exception as e:
                logger.error('models.ExtractArticle %s. pk: %s' % (str(e), oid))


def task_article_create():
    get_db_connection()
    stage = 'extract'
    model = 'article'
    r_queues = RQueues()

    collection = models.ExtractCollection.objects.all().first()

    for child in collection.children_ids:
        articles_ids = child['articles_ids']
        for article_pid in articles_ids:
            r_queues.enqueue(stage, model, task_extract_article, collection.acronym, article_pid)


# --------------------------------------------------- #
#               PRESS RELEASES                        #
# --------------------------------------------------- #


def task_extract_press_release(acronym, url, lang):
    extractor = PressReleaseExtractor(acronym, url, lang)
    pr_entries = extractor.get_feed_entries()
    for pr_entry in pr_entries:
        extractor.extract(pr_entry)
        extractor.save()


def task_press_release_update(ids=None):
    get_db_connection()
    stage = 'extract'
    model = 'press_release'
    r_queues = RQueues()

    if ids is None:  # update all collections
        models.ExtractPressRelease.objects.all().update(must_reprocess=True)
        for pr in models.ExtractPressRelease.objects.all():
            r_queues.enqueue(
                stage, model,
                task_extract_press_release,
                acronym=pr.journal_acronym,
                url=pr.feed_url_used,
                lang=pr.feed_lang)
    else:
        for oid in ids:
            try:
                obj = models.ExtractPressRelease.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(
                    stage, model,
                    task_extract_press_release,
                    acronym=obj.journal_acronym,
                    url=obj.feed_url_used,
                    lang=obj.feed_lang)
            except models.ExtractPressRelease.DoesNotExist as e:
                logger.error('models.ExtractPressRelease %s. pk: %s' % (str(e), oid))


def task_press_release_create():
    get_db_connection()
    stage = 'extract'
    model = 'press_release'
    r_queues = RQueues()

    for journal in models.ExtractJournal.objects.all():
        journal_dict = json.loads(journal.to_json())
        acronym = xylose_journal(journal_dict).acronym

        for lang, feed in config.RSS_PRESS_RELEASES_FEEDS_BY_CATEGORY.items():
            url = feed['url'].format(lang, acronym)
            r_queues.enqueue(
                stage, model,
                task_extract_press_release,
                acronym=acronym,
                url=url,
                lang=lang)

# --------------------------------------------------- #
#                    NEWS                             #
# --------------------------------------------------- #


def task_extract_news(url, lang):
    extractor = NewsExtractor(url, lang)
    news_entries = extractor.get_feed_entries()
    for news_entry in news_entries:
        extractor.extract(news_entry)
        extractor.save()


def task_news_update(ids=None):
    get_db_connection()
    stage = 'extract'
    model = 'news'
    r_queues = RQueues()

    if ids is None:  # update all collections
        models.ExtractNews.objects.all().update(must_reprocess=True)
        for news in models.ExtractNews.objects.all():
            r_queues.enqueue(
                stage, model,
                task_extract_news,
                url=news.feed_url_used,
                lang=news.feed_lang)
    else:
        for oid in ids:
            try:
                obj = models.ExtractNews.objects.get(pk=oid)
                obj.update(must_reprocess=True)
                obj.reload()
                r_queues.enqueue(
                    stage, model,
                    task_extract_news,
                    url=obj.feed_url_used,
                    lang=obj.feed_lang)
            except models.ExtractNews.DoesNotExist as e:
                logger.error('models.ExtractNews %s. pk: %s' % (str(e), oid))


def task_news_create():
    get_db_connection()
    stage = 'extract'
    model = 'news'
    r_queues = RQueues()

    for lang, feed in config.RSS_NEWS_FEEDS.items():
        url = feed['url'].format(lang)
        r_queues.enqueue(
            stage, model,
            task_extract_news,
            url=url,
            lang=lang)
