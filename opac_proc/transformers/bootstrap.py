# coding: utf-8
from __future__ import unicode_literals
# from redis import Redis
# from rq import Queue
# from rq.decorators import job

import logging
from opac_proc.logger_setup import config_logging
from opac_proc.datastore.mongodb_connector import get_db_connection

import config
from opac_proc.transformers.collections.transformation import CollectionTransformer
from opac_proc.transformers.journals.transformation import JournalTransformer
from opac_proc.transformers.issues.transformation import IssueTransformer
from opac_proc.transformers.articles.transformation import ArticleTransformer
from opac_proc.datastore.extract.models import ExtractCollection

# from opac_proc.extractors.jobs import (
#     task_extract_journal,
#     task_extract_issue,
#     task_extract_article
# )


logger = logging.getLogger(__name__)
# redis_conn = Redis()

# q_names = [
#     'qtr_journals',
#     'qtr_issues',
#     'qtr_articles',
# ]

# queues = {}
# for name in q_names:
#     queues[name] = Queue(name, connection=redis_conn)


def run(collection_acronym):
    db = get_db_connection()

    coll_transform = CollectionTransformer(
        extract_model_key=collection_acronym)
    coll_transform.transform()
    col = coll_transform.save()
    print u"Fim transformação da coleção!", col._id

    for child in col.children_ids:
        issn = child['issn']
        issues_ids = sorted(child['issues_ids'])
        articles_ids = sorted(child['articles_ids'])
        print "procurando issn: ", issn
        jtr = JournalTransformer(extract_model_key=issn)
        jtr.transform()
        jtr.save()

        for issue_id in issues_ids:
            print "procurando issue ", issue_id
            itr = IssueTransformer(extract_model_key=issue_id)
            itr.transform()
            itr.save()

        for article_id in articles_ids:
            print "procurando article ", article_id
            atr = ArticleTransformer(extract_model_key=article_id)
            atr.transform()
            atr.save()


if __name__ == '__main__':
    config_logging("DEBUG", "/Users/juanfunez/Work/Code/scielo.org/opac_proc/logs/q.logs")
    run('spa')
