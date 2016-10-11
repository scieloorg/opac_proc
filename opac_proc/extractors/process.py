# coding: utf-8
import time


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
    async = True
    db = get_db_connection()
    r_queues = RQueues()

    def __init__(self, collection_acronym=None, async=True):
        if collection_acronym:
            self.collection_acronym = collection_acronym
        else:
            self.collection_acronym = config.OPAC_PROC_COLLECTION

        self.async = async
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

    def reprocess_all(self):
        self.reprocess_collections()
        self.reprocess_journals()
        self.reprocess_issues()
        self.reprocess_articles()

    def process_collection(self, collection_acronym=None, collection_uuid=None):
        if not collection_acronym:
            collection_acronym = self.collection_acronym

        if collection_uuid is not None:
            uuid = str(collection_uuid)
        elif collection_acronym is not None:
            try:
                collection = models.ExtractCollection.objects.get(acronym=collection_acronym)
            except models.ExtractCollection.DoesNotExist:
                raise ValueError(u'ExtractCollection com acronym: %s não encontrado!' % collection_acronym)

            uuid = str(collection.uuid)
        else:
            raise ValueError("must provide at least one parameter: issn or uuid")

        if self.async:
            self.r_queues.enqueue(
                self.stage, 'collection',
                jobs.task_extract_collection,
                collection_acronym)
        else:
            # invocamos a task como funcão normal (sem fila)
            collection = jobs.task_extract_collection(collection_uuid=uuid)
            collection.reload()
            return collection

    def process_journal(self, collection_acronym=None, issn=None, uuid=None):
        if not collection_acronym:
            collection_acronym = self.collection_acronym

        if issn is not None:
            try:
                journal = models.ExtractJournal.objects.get(code=issn)
            except models.ExtractJournal.DoesNotExist:
                raise ValueError(u'ExtractJournal com code: %s não encontrado!' % issn)

            uuid = str(journal.uuid)

        elif uuid is not None:
            uuid = str(uuid)
        else:
            raise ValueError("must provide at least one parameter: issn or uuid")

        if self.async:
            self.r_queues.enqueue(
                self.stage, 'journal',
                jobs.task_extract_journal,
                collection_acronym,
                issn)
        else:
            # invocamos a task como funcão normal (sem fila)
            journal = jobs.task_extract_journal(collection_acronym, issn)
            journal.reload()
            return journal

    def process_issue(self, collection_acronym=None, issue_pid=None, uuid=None):
        if not collection_acronym:
            collection_acronym = self.collection_acronym

        if issue_pid is not None:
            try:
                issue = models.ExtractIssue.objects.get(pid=issue_pid)
            except models.ExtractIssue.DoesNotExist:
                raise ValueError(u'ExtractIssue com pid: %s não encontrado!' % issue_pid)

            uuid = str(issue.uuid)

        elif uuid is not None:
            uuid = str(uuid)
        else:
            raise ValueError("must provide at least one parameter: issn or uuid")

        if self.async:
            self.r_queues.enqueue(
                self.stage, 'issue',
                jobs.task_extract_issue,
                collection_acronym,
                issue_pid)
        else:
            # invocamos a task como funcão normal (sem fila)
            issue = jobs.task_extract_issue(
                collection_acronym, issue_pid)
            issue.reload()
            return issue

    def process_article(self, collection_acronym=None, article_pid=None, uuid=None):
        if not collection_acronym:
            collection_acronym = self.collection_acronym

        if article_pid is not None:
            try:
                article = models.ExtractArticle.objects.get(pid=article_pid)
            except models.ExtractArticle.DoesNotExist:
                raise ValueError(u'ExtractArticle com pid: %s não encontrado!' % issue_pid)

            uuid = str(article.uuid)

        elif uuid is not None:
            uuid = str(uuid)
        else:
            raise ValueError("must provide at least one parameter: issn or uuid")

        if self.async:
            self.r_queues.enqueue(
                self.stage, 'article',
                jobs.task_extract_article,
                collection_acronym,
                article_pid)
        else:
            # invocamos a task como funcão normal (sem fila)
            article = jobs.task_extract_article(
                collection_acronym, article_pid)
            articles.reload()
            return article

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

    def process_all(collection_acronym=None):
        logger.debug(u"Inicio process_all. collection_acronym = %s" % collection_acronym)
        if collection_acronym is None:
            collection_acronym = self.collection_acronym

        # processamos a coleção de forma asincrona pq devemos garantir que coleção extraida
        self.async = False
        logger.info(u'Extraindo Collection:  %s' % collection_acronym)
        collection = process_collection(collection_acronym)
        self.async = True  # o resto do processo deve ficar em tasks

        for child in collection.children_ids:
            issn = child['issn']
            issues_ids = child['issues_ids']
            articles_ids = child['articles_ids']

            logger.debug(u"enfilerando task: task_extract_journal [issn: %s]" % issn)
            process_journal(collection.acronym, issn)

            # processamos os issues com tasks
            for issue_id in issues_ids:
                logger.debug(u"enfilerando task: task_extract_issue [issue_id: %s]" % issue_id)
                process_issue(collection.acronym, issue_id)

            # processamos os articles com tasks
            for article_id in articles_ids:
                logger.debug(u"enfilerando task: task_extract_article [article_id: %s]" % article_id)
                process_article(collection.acronym, article_id)

        logger.debug(u"Fim enfileramento de tasks")
        logger.debug(u"Fim process_all")
