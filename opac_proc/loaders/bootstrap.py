# coding: utf-8
import os
import sys

import optparse
import textwrap
import logging

from mongoengine import Q

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.datastore.redis_queues import RQueues
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

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "load")
else:
    logger = getMongoLogger(__name__, "INFO", "load")

r_queues = RQueues()
r_queues.create_queues_for_stage('load')


def reprocess_collection(propagate=False):
    db = get_db_connection()
    for collection in LoadCollection.objects(must_reprocess=True):
        job = r_queues.enqueue(
            'load', 'collection',
            task_load_collection,
            collection.uuid)

        if propagate:
            reprocess_journal(depends_on=job, propagate=propagate)


def reprocess_journal(depends_on=None, propagate=False):
    db = get_db_connection()
    for journal in LoadJournal.objects(must_reprocess=True):

        if depends_on:
            job = r_queues.enqueue(
                'load', 'journal',
                task_load_journal,
                journal.uuid,
                depends_on=depends_on)
        else:
            job = r_queues.enqueue(
                'load', 'journal',
                task_load_journal,
                journal.uuid)

        if propagate:
            reprocess_issue(depends_on=job, propagate=propagate)


def reprocess_issue(depends_on=None, propagate=False):
    db = get_db_connection()
    for issue in LoadIssue.objects(must_reprocess=True):

        if depends_on:
            job = r_queues.enqueue(
                'load', 'issue',
                task_load_issue,
                issue.uuid,
                depends_on=depends_on)
        else:
            job = r_queues.enqueue(
                'load', 'issue',
                task_load_issue,
                issue.uuid)

        if propagate:
            reprocess_article(depends_on=job, propagate=propagate)


def reprocess_article(depends_on=None, propagate=False):
    db = get_db_connection()
    for article in LoadArticle.objects(must_reprocess=True):
        if depends_on:
            r_queues.enqueue(
                'load', 'article',
                task_load_article,
                article.uuid,
                depends_on=depends_on)
        else:
            r_queues.enqueue(
                'load', 'article',
                task_load_article,
                article.uuid)


def reprocess_all_pendings():
    register_connections()
    reprocess_collection()
    reprocess_journal()
    reprocess_issue()
    reprocess_article()


def load_all(collection_acronym):

    logger.info(u"iniciando load_all(%s)" % collection_acronym)
    db = get_db_connection()
    if not r_queues:
        logger.error(u'Não foram definidas as Queues')
        raise Exception(u'Não foram definidas as Queues')

    logger.info(u'Recuperando TransformCollection:  %s' % collection_acronym)
    coll_transform = TransformCollection.objects.get(
        acronym=collection_acronym)

    logger.info(u'Tranformando Collection:  %s' % collection_acronym)
    job_collection = r_queues.enqueue(
        'load', 'collection',
        task_load_collection,
        coll_transform.uuid)

    logger.info(u'Collection %s carregada' % coll_transform.acronym)
    logger.info(u"Disparando tasks")

    # for child in coll_transform.children_ids:
    #     issn = child['issn']
    #     issues_ids = child['issues_ids']
    #     articles_ids = child['articles_ids']

    #     logger.debug(u"recuperando periódico [issn: %s]" % issn)
    #     t_journal = TransformJournal.objects.get(Q(scielo_issn=issn) | Q(print_issn=issn) | Q(eletronic_issn=issn))

    #     logger.debug(u"enfilerando task: task_transform_journal [issn: %s]" % issn)
    #     job_journal = r_queues.enqueue(
    #         'load', 'journal',
    #         task_load_journal,
    #         t_journal.uuid)

    #     for issue_id in issues_ids:
    #         logger.debug(u"recuperando issue [pid: %s]" % issue_id)
    #         t_issue = TransformIssue.objects.get(pid=issue_id)
    #         logger.debug(u"enfilerando task: task_transform_issue [issue_id: %s]" % issue_id)
    #         job_issue = r_queues.enqueue(
    #             'load', 'issue',
    #             task_load_issue,
    #             t_issue.uuid)

    #         for t_article in TransformArticle.objects(issue=t_issue.uuid):
    #             logger.debug(u"enfilerando task: task_load_article [article_id: %s]" % t_article.pid)
    #             r_queues.enqueue(
    #                 'load', 'article',
    #                 task_load_article,
    #                 t_article.uuid)

    logger.info(u"Fim enfileramento de tasks")


def main(argv=sys.argv[1:]):
    usage = u"""\
    %prog Este processamento carrega todos os Journal, Issues, Articles transformados,
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

    # Nível do log
    parser.add_option(
        '--logging_level',
        '-l',
        default=config.OPAC_PROC_LOG_LEVEL,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help=u'Nível do log')

    options, args = parser.parse_args(argv)
    logger = getMongoLogger(__name__, options.logging_level, "load")

    try:
        if options.load_all and options.reprocess_all:
            logger.error(u"Operação inválida: --load-all e --reprocess-all são mutuamente exclusivos")
            exit(1)
        elif options.load_all:
            load_all(options.collection)
        elif options.reprocess_all:
            reprocess_all_pendings()
        else:
            logger.error(u"Operação inválida: deve indicar: --load-all ou --reprocess-all")
            exit(1)
    except KeyboardInterrupt:
        logger.info(u"Processamento interrompido pelo usuário.")


if __name__ == '__main__':
    main(sys.argv)
