# coding: utf-8
import time
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

    def reprocess_collection():
        collections = models.TransformCollection(must_reprocess=True)
        for collection in collections:
            self.process_collection(collection.code)

    def reprocess_journal():
        journals = models.TransformJournal(must_reprocess=True)
        for journal in journals:
            self.process_journal(self.collection_acronym, journal.code)

    def reprocess_issue():
        issues = models.TransformIssue(must_reprocess=True)
        for issue in issues:
            self.process_issue(self.collection_acronym, issue.code)

    def reprocess_article():
        articles = models.TransformArticle(must_reprocess=True)
        for article in articles:
            self.process_article(self.collection_acronym, article.code)

    def reprocess_all():
        # invocamos todos os metodos de reprocessar
        self.reprocess_collection()
        self.reprocess_journal()
        self.reprocess_issue()
        self.reprocess_article()

    def process_collection(collection_acronym=None):
        if not collection_acronym:
            collection_acronym = self.collection_acronym

        if self.async:
            self.r_queues.enqueue(
                self.stage, 'collection',
                jobs.task_transform_collection,
                collection_acronym)
        else:
            # invocamos a task como funcão normal (sem fila)
            collection = jobs.task_transform_collection(collection_acronym)
            collection.reload()
            return collection

    def process_journal(collection_acronym, issn):
        if self.async:
            self.r_queues.enqueue(
                self.stage, 'journal',
                jobs.task_transform_journal,
                collection_acronym,
                issn)
        else:
            # invocamos a task como funcão normal (sem fila)
            journal = jobs.task_transform_journal(
                collection_acronym, issn)
            journal.reload()
            return journal

    def process_issue(collection_acronym, issue_pid):
        if self.async:
            self.r_queues.enqueue(
                self.stage, 'issue',
                jobs.task_transform_issue,
                collection_acronym,
                issue_pid)
        else:
            # invocamos a task como funcão normal (sem fila)
            issue = jobs.task_transform_issue(
                collection_acronym, issue_pid)
            issue.reload()
            return issue

    def process_article(collection_acronym, article_pid):
        if self.async:
            self.r_queues.enqueue(
                self.stage, 'article',
                jobs.task_transform_article,
                collection_acronym,
                article_pid)
        else:
            # invocamos a task como funcão normal (sem fila)
            article = jobs.task_transform_article(
                collection_acronym, article_pid)
            articles.reload()
            return article

    def process_all(collection_acronym=None):
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
