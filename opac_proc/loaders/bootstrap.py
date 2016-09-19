# coding: utf-8
from __future__ import unicode_literals
from redis import Redis
from rq import Queue
import os
import sys
import optparse
import textwrap
import logging

from mongoengine import Q

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.web import config

from opac_proc.logger_setup import config_logging
from opac_proc.datastore.mongodb_connector import get_db_connection, register_connections
from opac_proc.datastore.models import (
    TransformCollection, LoadCollection,
    TransformJournal, LoadJournal,
    TransformIssue, LoadIssue,
    TransformArticle, LoadArticle)

from opac_proc.loaders.lo_collections import CollectionLoader
from opac_proc.loaders.lo_journals import JournalLoader
from opac_proc.loaders.lo_issues import IssueLoader
from opac_proc.loaders.lo_articles import ArticleLoader
from opac_proc.loaders.jobs import (
    task_load_collection,
    task_load_journal,
    task_load_issue,
    task_load_article)


logger = logging.getLogger(__name__)
redis_conn = Redis()

q_names = [
    'qlo_collections',
    'qlo_journals',
    'qlo_issues',
    'qlo_articles',
]

queues = {}
for name in q_names:
    queues[name] = Queue(name, connection=redis_conn)


def reprocess_collection(propagate=False):
    db = get_db_connection()
    for collection in LoadCollection.objects(must_reprocess=True):
        job = queues['qlo_collections'].enqueue(
            task_load_collection,
            collection.uuid)

        if propagate:
            reprocess_journal(depends_on=job, propagate=propagate)


def reprocess_journal(depends_on=None, propagate=False):
    db = get_db_connection()
    for journal in LoadJournal.objects(must_reprocess=True):

        if depends_on:
            job = queues['qlo_journals'].enqueue(
                task_load_journal,
                journal.uuid,
                depends_on=depends_on)
        else:
            job = queues['qlo_journals'].enqueue(
                task_load_journal,
                journal.uuid)

        if propagate:
            reprocess_issue(depends_on=job, propagate=propagate)


def reprocess_issue(depends_on=None, propagate=False):
    db = get_db_connection()
    for issue in LoadIssue.objects(must_reprocess=True):

        if depends_on:
            job = queues['qlo_issues'].enqueue(
                task_load_issue,
                issue.uuid,
                depends_on=depends_on)
        else:
            job = queues['qlo_issues'].enqueue(
                task_load_issue,
                issue.uuid)

        if propagate:
            reprocess_article(depends_on=job, propagate=propagate)


def reprocess_article(depends_on=None, propagate=False):
    db = get_db_connection()
    for article in LoadArticle.objects(must_reprocess=True):
        if depends_on:
            queues['qlo_articles'].enqueue(
                task_load_article,
                article.uuid,
                depends_on=depends_on)
        else:
            queues['qlo_articles'].enqueue(
                task_load_article,
                article.uuid)


def reprocess_all_pendings():
    register_connections()
    reprocess_collection()
    reprocess_journal()
    reprocess_issue()
    reprocess_article()


# def load_reprocess_journals():
#     t_journals = TransformJournal.objects(must)
#     for t_journal in t_journals:
#         j_loader = JournalLoader(t_journal.uuid)
#         opac_journal = j_loader.prepare()
#         print "opac_journal: ", opac_journal
#         j_loader.load()


# def load_issues():
#     t_issues = TransformIssue.objects.all()
#     for t_issue in t_issues:
#         i_loader = IssueLoader(t_issue.uuid)
#         opac_issue = i_loader.prepare()
#         print "opac_issue: ", opac_issue.label
#         i_loader.load()


# def load_articles():
#     t_articles = TransformArticle.objects.all()
#     for t_article in t_articles:
#         a_loader = ArticleLoader(t_article.uuid)
#         opac_article = a_loader.prepare()
#         print "opac_article: ", opac_article.title
#         a_loader.load()


def load_all(collection_acronym):
    db = get_db_connection()
    if not queues:
        logger.error('Não foram definidas as Queues')
        raise Exception(u'Não foram definidas as Queues')

    logger.info('Recuperando TransformCollection:  %s' % collection_acronym)
    coll_transform = TransformCollection.objects.get(
        acronym=collection_acronym)

    logger.info('Tranformando Collection:  %s' % collection_acronym)
    job_collection = queues['qlo_collections'].enqueue(
        task_load_collection,
        coll_transform.uuid)
    logger.info('Collection %s carregada' % coll_transform.acronym)
    logger.info("Disparando tasks")

    for child in coll_transform.children_ids:
        issn = child['issn']
        issues_ids = child['issues_ids']
        articles_ids = child['articles_ids']

        logger.debug("recuperando periódico [issn: %s]" % issn)
        t_journal = TransformJournal.objects.get(Q(scielo_issn=issn) | Q(print_issn=issn) | Q(eletronic_issn=issn))
        logger.debug("enfilerando task: task_transform_journal [issn: %s]" % issn)
        job_journal = queues['qlo_journals'].enqueue(
                task_load_journal,
                t_journal.uuid,
                depends_on=job_collection)

        for issue_id in issues_ids:
            logger.debug("recuperando issue [pid: %s]" % issue_id)
            t_issue = TransformIssue.objects.get(pid=issue_id)
            logger.debug("enfilerando task: task_transform_issue [issue_id: %s]" % issue_id)
            job_issue = queues['qlo_issues'].enqueue(
                task_load_issue,
                t_issue.uuid,
                depends_on=job_journal)

            for t_article in TransformArticle.objects(issue=t_issue.uuid):
                logger.debug("enfilerando task: task_load_article [article_id: %s]" % t_article.pid)
                queues['qlo_articles'].enqueue(
                    task_load_article,
                    t_article.uuid,
                    depends_on=job_issue)

    logger.info("Fim enfileramento de tasks")


def main(argv=sys.argv[1:]):
    usage = u"""\
    %prog Este processamento coleta todos os Journal, Issues, Articles transformados,
    e armazenda os dados em um banco MongoDB do OPAC, que serão exposto pelo OPAC.
    """

    parser = optparse.OptionParser(
        textwrap.dedent(usage), version=u"version: 1.0")

    parser.add_option(
        '--collection',
        '-c',
        dest='collection',
        default=config.OPAC_PROC_COLLECTION,
        help=u'Acronimo da coleção. Por exemplo: spa, scl, col.')

    parser.add_option(
        '--load_all',
        '-a',
        dest='load_all',
        default=False,
        help=u'Carregar tudo: coleções,periódicos,fascículos e artigos')

    parser.add_option(
        '--reprocess-all',
        '-r',
        dest='reprocess_all',
        default=False,
        help=u'Reprocessar tudo')

    # Arquivo de log
    parser.add_option(
        '--logging_file',
        '-o',
        default=config.OPAC_PROC_LOG_FILE_PATH,
        help=u'Caminho absoluto do log file')

    # Nível do log
    parser.add_option(
        '--logging_level',
        '-l',
        default=config.OPAC_PROC_LOG_LEVEL,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help=u'Nível do log')

    options, args = parser.parse_args(argv)
    config_logging(options.logging_level, options.logging_file)

    try:
        if options.load_all and options.reprocess_all:
            logger.error("Operação inválida: --load-all e --reprocess-all são mutuamente exclusivos")
            exit(1)
        elif options.load_all:
            load_all(options.collection)
        elif options.reprocess_all:
            reprocess_all_pendings()
        else:
            logger.error("Operação inválida: deve indicar: --load-all ou --reprocess-all")
            exit(1)
    except KeyboardInterrupt:
        logger.info(u"Processamento interrompido pelo usuário.")


if __name__ == '__main__':
    main(sys.argv)
