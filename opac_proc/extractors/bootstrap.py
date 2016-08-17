# coding: utf-8
from __future__ import unicode_literals
from redis import Redis
from rq import Queue
from rq.decorators import job

import logging
from opac_proc.logger_setup import config_logging
from opac_proc.datastore.mongodb_connector import get_db_connection

import config
from opac_proc.extractors.collections.extraction import ColectionExtactor
from opac_proc.extractors.jobs import (
    task_extract_journal,
    task_extract_issue,
    task_extract_article
)


logger = logging.getLogger(__name__)
redis_conn = Redis()

q_names = [
    'qex_journals',
    'qex_issues',
    'qex_articles',
]

queues = {}
for name in q_names:
    queues[name] = Queue(name, connection=redis_conn)


def run(collection_acronym):
    db = get_db_connection()
    db_name = config.MONGODB_SETTINGS['db']
    db.drop_database(db_name)
    print "banco de dados removido!"
    coll_extractor = ColectionExtactor(collection_acronym)
    coll_extractor.extract()
    print "Fim da coleta da Coleção"
    col = coll_extractor.save()
    print "Fim do save() da Coleção"
    print "Disparando tasks"

    if not queues:
        raise Exception(u'Não foram definidas as Queues')

    for child in col.children_ids:
        issn = child['issn']
        issues_ids = child['issues_ids']
        articles_ids = child['articles_ids']

        job_ex_jounal = queues['qex_journals'].enqueue(
            task_extract_journal,
            collection_acronym, issn)

        for issue_id in issues_ids:
            job_ex_issue = queues['qex_issues'].enqueue(
                task_extract_issue,
                collection_acronym,
                issue_id)

        for article_id in articles_ids:
            job_ex_article = queues['qex_articles'].enqueue(
                task_extract_article,
                collection_acronym,
                article_id)

    print "Fim!"

if __name__ == '__main__':
    config_logging("DEBUG", "/Users/juanfunez/Work/Code/scielo.org/opac_proc/logs/q.logs")
    run('spa')
