# coding: utf-8
import logging
from datetime import datetime

from opac_proc.datastore.transform.models import (
    TransformCollection, TransformJournal,
    TransformIssue, TransformArticle)
from opac_proc.loaders.collections.load import CollectionLoader
from opac_proc.loaders.journals.load import JournalLoader
from opac_proc.loaders.issues.load import IssueLoader
from opac_proc.loaders.articles.load import ArticleLoader
from opac_schema.v1.models import Collection as OpacCollection
from opac_proc.logger_setup import config_logging
from opac_proc.datastore.mongodb_connector import get_db_connection

logger = logging.getLogger(__name__)


def load_journals():
    t_journals = TransformJournal.objects.all()
    for t_journal in t_journals:
        j_loader = JournalLoader(t_journal.uuid)
        opac_journal = j_loader.prepare()
        print "opac_journal: ", opac_journal
        j_loader.load()


def load_issues():
    t_issues = TransformIssue.objects.all()
    for t_issue in t_issues:
        i_loader = IssueLoader(t_issue.uuid)
        opac_issue = i_loader.prepare()
        print "opac_issue: ", opac_issue.label
        i_loader.load()


def load_articles():
    t_articles = TransformArticle.objects.all()
    for t_article in t_articles:
        a_loader = ArticleLoader(t_article.uuid)
        opac_article = a_loader.prepare()
        print "opac_article: ", opac_article.title
        a_loader.load()


def run(collection_acronym):
    db = get_db_connection()
    coll_transform = TransformCollection.objects.get(
        acronym=collection_acronym)

    coll_loader = CollectionLoader(coll_transform.uuid)
    opac_coll = coll_loader.prepare()
    print "opac_coll: ", opac_coll
    coll_loader.load()

    print "JOURNALS:"
    load_journals()
    print "ISSUES:"
    load_issues()
    print "ARTICLES:"
    load_articles()()
    print "fim!"


if __name__ == '__main__':
    config_logging("DEBUG", "/Users/juanfunez/Work/Code/scielo.org/opac_proc/logs/q.logs")
    run('spa')
