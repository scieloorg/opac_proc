# coding: utf-8
from opac_proc.core.process import Process

from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import get_db_connection

from opac_proc.datastore import models
from opac_proc.transformers import jobs

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "transform")
else:
    logger = getMongoLogger(__name__, "INFO", "transform")


class TransformProcess(Process):
    stage = 'transform'
    collection_acronym = None
    db = get_db_connection()
    r_queues = RQueues()

    def __init__(self, collection_acronym=None):
        if collection_acronym:
            self.collection_acronym = collection_acronym
        else:
            self.collection_acronym = config.OPAC_PROC_COLLECTION

        self.r_queues.create_queues_for_stage(self.stage)

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

    def process_collection(self, collection_acronym=None, collection_uuid=None):
        if not collection_acronym:
            collection_acronym = self.collection_acronym

        if collection_uuid is None:  # buscamos a coleção pelo Acronimo
            try:
                collection = models.TransformCollection.objects.get(acronym=collection_acronym)
            except models.TransformCollection.DoesNotExist:
                raise ValueError(u'TransformCollection com acronym: %s não encontrado!' % collection_acronym)
        elif collection_acronym:
            try:
                collection = models.TransformCollection.objects.get(uuid=collection_uuid)
            except models.TransformCollection.DoesNotExist:
                raise ValueError(u'TransformCollection com uuid: %s não encontrado!' % collection_uuid)
        else:
            raise ValueError("must provide at least one parameter: issn or uuid")

        collection_acronym = collection.acronym

        self.r_queues.enqueue(
            self.stage, 'collection',
            jobs.task_transform_collection,
            collection_acronym)

    def process_journal(self, collection_acronym=None, issn=None, uuid=None):
        if not collection_acronym:
            collection_acronym = self.collection_acronym

        if issn is not None:
            try:
                journal = models.TransformJournal.objects.get(code=issn)
            except models.TransformJournal.DoesNotExist:
                raise ValueError(u'TransformJournal com code: %s não encontrado!' % issn)

            uuid = str(journal.uuid)

        elif uuid is not None:
            uuid = str(uuid)
        else:
            raise ValueError("must provide at least one parameter: issn or uuid")

        self.r_queues.enqueue(
            self.stage, 'journal',
            jobs.task_transform_journal,
            collection_acronym,
            issn)

    def process_issue(self, collection_acronym=None, issue_pid=None, uuid=None):
        if not collection_acronym:
            collection_acronym = self.collection_acronym

        if issue_pid is not None:
            try:
                issue = models.TransformIssue.objects.get(pid=issue_pid)
            except models.TransformIssue.DoesNotExist:
                raise ValueError(u'TransformIssue com pid: %s não encontrado!' % issue_pid)

            uuid = str(issue.uuid)

        elif uuid is not None:
            uuid = str(uuid)
        else:
            raise ValueError("must provide at least one parameter: issn or uuid")

        self.r_queues.enqueue(
            self.stage, 'issue',
            jobs.task_transform_issue,
            collection_acronym,
            issue_pid)

    def process_article(self, collection_acronym=None, article_pid=None, uuid=None):
        if not collection_acronym:
            collection_acronym = self.collection_acronym

        if article_pid is not None:
            try:
                article = models.TransformArticle.objects.get(pid=article_pid)
            except models.TransformArticle.DoesNotExist:
                raise ValueError(u'TransformArticle com pid: %s não encontrado!' % article_pid)

            uuid = str(article.uuid)

        elif uuid is not None:
            uuid = str(uuid)
        else:
            raise ValueError("must provide at least one parameter: issn or uuid")

        self.r_queues.enqueue(
            self.stage, 'article',
            jobs.task_transform_article,
            collection_acronym,
            article_pid)

    def process_all_collections(self):
        self.r_queues.enqueue(
            self.stage, 'collection', jobs.task_process_all_collections, self.collection_acronym)

    def process_all_journals(self):
        self.r_queues.enqueue(
            self.stage, 'journal', jobs.task_process_all_journals)

    def process_all_issues(self):
        self.r_queues.enqueue(
            self.stage, 'issue', jobs.task_process_all_issues)

    def process_all_articles(self):
        self.r_queues.enqueue(
            self.stage, 'issue', jobs.task_process_all_articles)
