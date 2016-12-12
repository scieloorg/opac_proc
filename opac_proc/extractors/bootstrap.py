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
    ExtractJournal,
    ExtractIssue,
    ExtractArticle)

from opac_proc.extractors.ex_collections import CollectionExtactor
from opac_proc.extractors.jobs import (
    task_extract_collection,
    task_extract_journal,
    task_extract_issue,
    task_extract_article)

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "extract")
else:
    logger = getMongoLogger(__name__, "INFO", "extract")

r_queues = RQueues()
r_queues.create_queues_for_stage('extract')


def reprocess_collection(collection_acronym):
    for collection in ExtractCollection.objects(must_reprocess=True):
        r_queues.enqueue(
            'extract', 'collection',
            task_extract_collection,
            collection.acronym)


def reprocess_journal(collection_acronym):
    for ex_journal in ExtractJournal.objects(must_reprocess=True):
        r_queues.enqueue(
            'extract', 'journal',
            task_extract_journal,
            collection_acronym,
            ex_journal.code)


def reprocess_issue(collection_acronym):
    for ex_issue in ExtractIssue.objects(must_reprocess=True):
        r_queues.enqueue(
            'extract', 'issue',
            task_extract_issue,
            collection_acronym,
            ex_issue.code)


def reprocess_article(collection_acronym):
    for ex_article in ExtractArticle.objects(must_reprocess=True):
        r_queues.enqueue(
            'extract', 'article',
            task_extract_article,
            collection_acronym,
            ex_article.code)


def reprocess_all_pendings(collection_acronym):
    db = get_db_connection()
    reprocess_collection(collection_acronym)
    reprocess_journal(collection_acronym)
    reprocess_issue(collection_acronym)
    reprocess_article(collection_acronym)


def extract_all(collection_acronym):
    db = get_db_connection()
    db_name = config.MONGODB_SETTINGS['db']
    logger.info(u'Extraindo Collection:  %s' % collection_acronym)
    coll_extractor = CollectionExtactor(collection_acronym)
    coll_extractor.extract()
    col = coll_extractor.save()
    logger.info(u'Collection %s extraida' % col.acronym)
    logger.info(u'Disparando tasks')

    if not r_queues:
        logger.error(u'Não foram definidas as Queues')
        raise Exception(u'Não foram definidas as Queues')

    for child in col.children_ids:
        issn = child['issn']
        issues_ids = child['issues_ids']
        articles_ids = child['articles_ids']

        logger.debug(u"enfilerando task: task_extract_journal [issn: %s]" % issn)
        r_queues.enqueue(
            'extract', 'journal',
            task_extract_journal,
            collection_acronym,
            issn)

        for issue_id in issues_ids:
            logger.debug(u"enfilerando task: task_extract_issue [issue_id: %s]" % issue_id)
            r_queues.enqueue(
                'extract', 'issue',
                task_extract_issue,
                collection_acronym,
                issue_id)

        for article_id in articles_ids:
            logger.debug(u"enfilerando task: task_extract_article [article_id: %s]" % article_id)
            r_queues.enqueue(
                'extract', 'article',
                task_extract_article,
                collection_acronym,
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
        '--extract-all',
        '-e',
        dest='extract_all',
        default=False,
        help=u'Extair tudo: coleções,periódicos,fascículos e artigos')

    parser.add_option(
        '--reprocess-all',
        '-r',
        dest='reprocess_all',
        default=False,
        help=u'Reprocessar todos os registros de Extração')

    # Nível do log
    parser.add_option(
        '--logging_level',
        '-l',
        default=config.OPAC_PROC_LOG_LEVEL,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help=u'Nível do log')

    options, args = parser.parse_args(argv)
    logger = getMongoLogger(__name__, options.logging_level, "extract")

    try:
        if options.extract_all and options.reprocess_all:
            logger.error(u"Operação inválida: --extract-all e --reprocess-all são mutuamente exclusivos")
            exit(1)
        elif options.extract_all:
            extract_all(options.collection)
        elif options.reprocess_all:
            reprocess_all_pendings(options.collection)
        else:
            logger.error(u"Operação inválida: deve indicar: --extract-all ou --reprocess-all")
            exit(1)
    except KeyboardInterrupt:
        logger.info(u"Processamento interrompido pelo usuário.")


if __name__ == '__main__':
    main(sys.argv)
