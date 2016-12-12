# coding: utf-8
import os
import sys

import optparse
import textwrap

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.datastore.redis_queues import RQueues
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

r_queues = RQueues()
r_queues.create_queues_for_stage('transform')


def reprocess_collection(collection_acronym):
    for collection in TransformCollection(must_reprocess=True):
        r_queues.enqueue(
            'transform', 'collection',
            task_transform_collection,
            collection.code)


def reprocess_journal():
    for tr_journal in TransformJournal(must_reprocess=True):
        r_queues.enqueue(
            'transform', 'journal',
            task_transform_journal,
            tr_journal.code)


def reprocess_issue():
    for tr_issue in TransformIssue(must_reprocess=True):
        r_queues.enqueue(
            'transform', 'issue',
            task_transform_issue,
            tr_issue.code)


def reprocess_article():
    for tr_article in TransformArticle(must_reprocess=True):
        r_queues.enqueue(
            'transform', 'article',
            task_transform_article,
            tr_article.code)


def reprocess_all_pendings(collection_acronym):
    db = get_db_connection()
    reprocess_collection(collection_acronym)
    reprocess_journal()
    reprocess_issue()
    reprocess_article()


def transform_all(collection_acronym):
    logger.info(u'inciando transform_all(%s)' % collection_acronym)
    db = get_db_connection()
    col = ExtractCollection.objects.get(acronym=collection_acronym)

    if not r_queues:
        msg = u'Não foram definidas as Queues'
        logger.error(msg)
        raise RuntimeError(msg)

    logger.debug(u'enfilerando task: task_transform_collection')
    r_queues.enqueue(
        'transform', 'collection',
        task_transform_collection,
        col.acronym)

    try:
        logger.debug(u'Tentamos recuperar a coleção transformada')
        col = TransformCollection.objects.get(acronym=collection_acronym)
    except Exception as e:
        logger.debug(u'Erro tentando recuperar a coleção transformada. (a task terminou?) Continuamos com a coleção extradia')
        pass

    logger.info(u'Collection %s tranformada' % col.acronym)

    logger.info(u'Disparando tasks')
    for child in col.children_ids:
        issn = child['issn']
        issues_ids = child['issues_ids']
        articles_ids = child['articles_ids']

        logger.debug(u"enfilerando task: task_transform_journal [issn: %s]" % issn)
        r_queues.enqueue(
            'transform', 'journal',
            task_transform_journal,
            issn)

        for issue_id in issues_ids:
            logger.debug(u"enfilerando task: task_transform_issue [issue_id: %s]" % issue_id)
            r_queues.enqueue(
                'transform', 'issue',
                task_transform_issue,
                issue_id)

        for article_id in articles_ids:
            logger.debug(u"enfilerando task: task_transform_article [article_id: %s]" % article_id)
            r_queues.enqueue(
                'transform', 'article',
                task_transform_article,
                article_id)

    logger.info(u"Fim enfileramento de tasks")


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
            logger.error(u"Operação inválida: --transform-all e --reprocess-all são mutuamente exclusivos")
            exit(1)
        elif options.transform_all:
            transform_all(options.collection)
        elif options.reprocess_all:
            reprocess_all_pendings(options.collection)
        else:
            logger.error(u"Operação inválida: deve indicar: --transform-all ou --reprocess-all")
            exit(1)
    except KeyboardInterrupt:
        logger.info(u"Processamento interrompido pelo usuário.")


if __name__ == '__main__':
    main(sys.argv)
