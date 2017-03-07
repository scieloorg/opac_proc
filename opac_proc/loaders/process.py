# coding: utf-8
from mongoengine import Q

from opac_proc.core.process import Process
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import get_db_connection

from opac_proc.datastore import models
from opac_proc.loaders import jobs

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "load")
else:
    logger = getMongoLogger(__name__, "INFO", "load")


class LoadProcess(Process):
    stage = 'load'
    collection_acronym = None
    db = get_db_connection()
    r_queues = RQueues()

    def __init__(self, collection_acronym=None):
        if collection_acronym:
            self.collection_acronym = collection_acronym
        else:
            self.collection_acronym = config.OPAC_PROC_COLLECTION

        self.r_queues.create_queues_for_stage(self.stage)

    # Reprocess

    def reprocess_collections(self, ids=None):
        self.r_queues.enqueue(
            self.stage, 'collection', jobs.task_reprocess_collections, ids)

    def reprocess_journals(self, ids=None):
        self.r_queues.enqueue(
            self.stage, 'journal', jobs.task_reprocess_journals, ids)

    def reprocess_issues(self, ids=None):
        self.r_queues.enqueue(
            self.stage, 'issue', jobs.task_reprocess_issues, ids)

    def reprocess_articles(self, ids=None):
        self.r_queues.enqueue(
            self.stage, 'article', jobs.task_reprocess_articles, ids)

    def reprocess_press_releases(self, ids=None):
        self.r_queues.enqueue(
            self.stage, 'press_release', jobs.task_reprocess_press_releases, ids)

    # Process

    def process_collection(self, collection_acronym=None, collection_uuid=None):
        if not collection_acronym:
            collection_acronym = self.collection_acronym

        if collection_uuid is not None:
            uuid = str(collection_uuid)
        else:
            try:
                collection = models.LoadCollection.objects.get(acronym=collection_acronym)
            except models.LoadCollection.DoesNotExist:
                collection = models.TransformCollection.objects.get(acronym=collection_acronym)

            uuid = str(collection.uuid)

        self.r_queues.enqueue(
            self.stage, 'collection',
            jobs.task_load_collection,
            uuid)

    def process_journal(self, collection_acronym=None, issn=None, uuid=None):
        if not collection_acronym:
            collection_acronym = self.collection_acronym

        if issn is not None:
            try:
                journal = models.LoadJournal.objects.get(issn=issn)
            except models.LoadJournal.DoesNotExist:
                journal = models.TransformJournal.objects.get(
                    Q(scielo_issn=issn) | Q(print_issn=issn) | Q(eletronic_issn=issn))

            uuid = str(journal.uuid)

        elif uuid is not None:
            uuid = str(uuid)
        else:
            raise ValueError("must provide at least one parameter: issn or uuid")

        self.r_queues.enqueue(
            self.stage, 'journal',
            jobs.task_load_journal,
            uuid)

    def process_issue(self, collection_acronym=None, issue_pid=None, uuid=None):
        if not collection_acronym:
            collection_acronym = self.collection_acronym

        if issue_pid is not None:
            try:
                issue = models.LoadIssue.objects.get(pid=issue_pid)
            except models.LoadIssue.DoesNotExist:
                issue = models.TransformIssue.objects.get(pid=issue_pid)

            uuid = str(issue.uuid)

        elif uuid is not None:
            uuid = str(uuid)
        else:
            raise ValueError("must provide at least one parameter: issn or uuid")

        self.r_queues.enqueue(
            self.stage, 'issue',
            jobs.task_load_issue,
            uuid)

    def process_article(self, collection_acronym=None, article_pid=None, uuid=None):
        if not collection_acronym:
            collection_acronym = self.collection_acronym

        if article_pid is not None:
            try:
                article = models.LoadArticle.objects.get(pid=article_pid)
            except models.LoadIssue.DoesNotExist:
                article = models.TransformArticle.objects.get(pid=article_pid)

            uuid = str(article.uuid)

        elif uuid is not None:
            uuid = str(uuid)
        else:
            raise ValueError("must provide at least one parameter: issn or uuid")

        self.r_queues.enqueue(
            self.stage, 'article',
            jobs.task_load_article,
            uuid)

    def process_press_release(self, uuid):
        self.r_queues.enqueue(
            self.stage, 'press_release',
            jobs.task_load_press_release,
            uuid=uuid)

    # Process All

    def process_all_collections(self):
        self.r_queues.enqueue(
            self.stage, 'collection', jobs.task_process_all_collections)

    def process_all_journals(self):
        self.r_queues.enqueue(
            self.stage, 'journal', jobs.task_process_all_journals)

    def process_all_issues(self):
        self.r_queues.enqueue(
            self.stage, 'issue', jobs.task_process_all_issues)

    def process_all_articles(self):
        self.r_queues.enqueue(
            self.stage, 'issue', jobs.task_process_all_articles)

    def process_all_press_releases(self):
        self.r_queues.enqueue(
            self.stage, 'press_release', jobs.task_process_all_press_releases)
