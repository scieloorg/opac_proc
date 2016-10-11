# coding: utf-8
import time
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
        else:
            try:
                collection = models.LoadCollection.objects.get(acronym=collection_acronym)
            except models.LoadCollection.DoesNotExist:
                collection = models.TransformCollection.objects.get(acronym=collection_acronym)

            uuid = str(collection.uuid)

        if self.async:
            self.r_queues.enqueue(
                self.stage, 'collection',
                jobs.task_load_collection,
                uuid)
        else:
            # invocamos a task como funcão normal (sem fila)
            collection = jobs.task_load_collection(uuid)
            collection.reload()
            return collection

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

        if self.async:
            self.r_queues.enqueue(
                self.stage, 'journal',
                jobs.task_load_journal,
                uuid)
        else:
            # invocamos a task como funcão normal (sem fila)
            journal = jobs.task_load_journal(uuid)
            journal.reload()
            return journal

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

        if self.async:
            self.r_queues.enqueue(
                self.stage, 'issue',
                jobs.task_load_issue,
                uuid)
        else:
            # invocamos a task como funcão normal (sem fila)
            issue = jobs.task_load_issue(
                collection_acronym, uuid)
            issue.reload()
            return issue

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

        if self.async:
            self.r_queues.enqueue(
                self.stage, 'article',
                jobs.task_load_article,
                uuid)
        else:
            # invocamos a task como funcão normal (sem fila)
            article = jobs.task_transform_article(
                jobs.task_load_article, uuid)
            articles.reload()
            return article

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

    def process_all(self, collection_acronym=None):
        logger.debug(u"Inicio process_all. collection_acronym = %s" % collection_acronym)
        if collection_acronym is None:
            collection_acronym = self.collection_acronym

        # processamos a coleção de forma asincrona pq devemos garantir que coleção extraida
        self.async = False
        logger.info(u'Transoformando Collection:  %s' % collection_acronym)
        collection = process_collection(collection_acronym)
        self.async = True  # o resto do processo deve ficar em tasks

        for child in collection.children_ids:
            issn = child['issn']
            issues_ids = child['issues_ids']
            articles_ids = child['articles_ids']

            logger.debug(u"enfilerando task: task_extract_journal [issn: %s]" % issn)
            process_journal(collection.acronym, issn=issn)

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
