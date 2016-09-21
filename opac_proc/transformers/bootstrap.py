# coding: utf-8
import os
import sys
from redis import Redis
from rq import Queue

import optparse
import textwrap
import logging

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.datastore.models import (
    ExtractCollection,
    TransformCollection,
    TransformJournal,
    TransformIssue,
    TransformArticle)

from opac_proc.transformers.tr_collections import CollectionTransformer
from opac_proc.transformers.jobs import (
    task_transform_collection,
    task_transform_journal,
    task_transform_issue,
    task_transform_article)

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "transform")
else:
    logger = getMongoLogger(__name__, "INFO", "transform")

redis_conn = Redis()

q_names = [
    'qtr_collections',
    'qtr_journals',
    'qtr_issues',
    'qtr_articles',
]

queues = {}
for name in q_names:
    queues[name] = Queue(name, connection=redis_conn)


def reprocess_collection(collection_acronym):
    for collection in TransformCollection.objects(must_reprocess=True):
        queues['qtr_collections'].enqueue(
            task_transform_collection,
            collection.acronym)


def reprocess_journal(collection_acronym):
    for tr_journal in TransformJournal.objects(must_reprocess=True):
        queues['qtr_journals'].enqueue(
            task_extract_journal,
            collection_acronym, tr_journal.code)


def reprocess_issue(collection_acronym):
    for tr_issue in TransformIssue.objects(must_reprocess=True):
        queues['qtr_issues'].enqueue(
            task_extract_issue,
            collection_acronym, tr_issue.code)


def reprocess_article(collection_acronym):
    for tr_article in TransformArticle.objects(must_reprocess=True):
        queues['qtr_articles'].enqueue(
            task_extract_article,
            collection_acronym, tr_article.code)


def reprocess_all_pendings(collection_acronym):
    db = get_db_connection()
    reprocess_collection(collection_acronym)
    reprocess_journal(collection_acronym)
    reprocess_issue(collection_acronym)
    reprocess_article(collection_acronym)


def transform_all(collection_acronym):
    db = get_db_connection()
    logger.info('Tranformando Collection:  %s' % collection_acronym)
    coll_transform = CollectionTransformer(
        extract_model_key=collection_acronym)
    coll_transform.transform()
    col = coll_transform.save()
    logger.info('Collection %s tranformada' % col.acronym)
    logger.info("Disparando tasks")

    if not queues:
        logger.error('Não foram definidas as Queues')
        raise Exception(u'Não foram definidas as Queues')

    for child in col.children_ids:
        issn = child['issn']
        issues_ids = child['issues_ids']
        articles_ids = child['articles_ids']

        logger.debug("enfilerando task: task_transform_journal [issn: %s]" % issn)
        queues['qtr_journals'].enqueue(
            task_transform_journal,
            issn)

        for issue_id in issues_ids:
            logger.debug("enfilerando task: task_transform_issue [issue_id: %s]" % issue_id)
            queues['qtr_issues'].enqueue(
                task_transform_issue,
                issue_id)

        for article_id in articles_ids:
            logger.debug("enfilerando task: task_transform_article [article_id: %s]" % article_id)
            queues['qtr_articles'].enqueue(
                task_transform_article,
                article_id)

    logger.info("Fim enfileramento de tasks")


def main(argv=sys.argv[1:]):
    usage = u"""\
    %prog Este processamento coleta todos os Journal, Issues, Articles do Article meta,
    de uma determinada coleção, armazenando estes dados em um banco MongoDB,
    que serão exposto pelo OPAC.
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
        '--transform-all',
        '-t',
        dest='transform_all',
        default=False,
        help=u'Transformar tudo: coleções,periódicos,fascículos e artigos')

    parser.add_option(
        '--reprocess-all',
        '-r',
        dest='reprocess_all',
        default=False,
        help=u'Reprocessar todos os registros de Transformação')

    # Nível do log
    parser.add_option(
        '--logging_level',
        '-l',
        default=config.OPAC_PROC_LOG_LEVEL,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help=u'Nível do log')

    options, args = parser.parse_args(argv)
    logger = getMongoLogger(__name__, options.logging_level, "transform")

    try:
        if options.transform_all and options.reprocess_all:
            logger.error("Operação inválida: --transform-all e --reprocess-all são mutuamente exclusivos")
            exit(1)
        elif options.transform_all:
            transform_all(options.collection)
        elif options.reprocess_all:
            reprocess_all_pendings(options.collection)
        else:
            logger.error("Operação inválida: deve indicar: --transform-all ou --reprocess-all")
            exit(1)
    except KeyboardInterrupt:
        logger.info(u"Processamento interrompido pelo usuário.")


if __name__ == '__main__':
    main(sys.argv)
