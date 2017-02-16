# coding: utf-8
from opac_proc.core.process import Process

from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import get_db_connection

from opac_proc.datastore import models
from opac_proc.extractors import jobs

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "extract")
else:
    logger = getMongoLogger(__name__, "INFO", "extract")


class ExtractProcess(Process):
    stage = 'extract'
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
        if collection_acronym is None and collection_uuid is None:
            collection_acronym = self.collection_acronym
        elif collection_acronym is None:  # collection_uuid tem algum valor != None
            try:
                collection = models.ExtractCollection.objects.get(uuid=collection_uuid)
            except models.ExtractCollection.DoesNotExist:
                raise ValueError(u'ExtractCollection com uuid: %s não encontrado!' % collection_uuid)
            else:
                collection_acronym = collection.acronym

        # collection_acronym tem um acrônimo
        self.r_queues.enqueue(
            self.stage, 'collection',
            jobs.task_extract_collection,
            collection_acronym)

    def process_journal(self, collection_acronym=None, issn=None, uuid=None):
        if not collection_acronym:
            collection_acronym = self.collection_acronym

        if issn is not None:
            try:
                journal = models.ExtractJournal.objects.get(code=issn)
            except models.ExtractJournal.DoesNotExist:
                raise ValueError(u'ExtractJournal com code: %s não encontrado!' % issn)
        else:
            raise ValueError("must provide at least one parameter: issn or uuid")

        self.r_queues.enqueue(
            self.stage, 'journal',
            jobs.task_extract_journal,
            collection_acronym,
            issn)

    def process_issue(self, collection_acronym=None, issue_pid=None, uuid=None):
        if not collection_acronym:
            collection_acronym = self.collection_acronym

        if issue_pid is not None:
            # TODO: Remover este código pois não está sendo utilizado
            # Sugestão de Refatoração:
            # if issue_pid is None:
            #     raise ValueError("must provide at least one parameter: issn or uuid")
            try:
                issue = models.ExtractIssue.objects.get(pid=issue_pid)
            except models.ExtractIssue.DoesNotExist:
                raise ValueError(u'ExtractIssue com pid: %s não encontrado!' % issue_pid)

            uuid = str(issue.uuid)

        elif uuid is not None:
            uuid = str(uuid)
        else:
            raise ValueError("must provide at least one parameter: issn or uuid")

        self.r_queues.enqueue(
            self.stage, 'issue',
            jobs.task_extract_issue,
            collection_acronym,
            issue_pid)

    def process_article(self, collection_acronym=None, article_pid=None, uuid=None):
        if not collection_acronym:
            collection_acronym = self.collection_acronym

        if article_pid is not None:
            try:
                article = models.ExtractArticle.objects.get(pid=article_pid)
            except models.ExtractArticle.DoesNotExist:
                raise ValueError(u'ExtractArticle com pid: %s não encontrado!' % article_pid)

            uuid = str(article.uuid)

        elif uuid is not None:
            uuid = str(uuid)
        else:
            raise ValueError("must provide at least one parameter: issn or uuid")

        self.r_queues.enqueue(
            self.stage, 'article',
            jobs.task_extract_article,
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
            self.stage, 'article', jobs.task_process_all_articles)

    def process_all_press_releases(self):
        jobs.task_process_all_press_releases()
        self.r_queues.enqueue(
            self.stage, 'press_release', jobs.task_process_all_press_releases)
