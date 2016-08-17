# coding: utf-8
from __future__ import unicode_literals

import logging

from opac_proc.extractors.journals.extraction import JournalExtactor
from opac_proc.extractors.issues.extraction import IssueExtactor
from opac_proc.extractors.articles.extraction import ArticleExtactor

logger = logging.getLogger(__name__)


def task_extract_journal(acronym, issn):
    extractor = JournalExtactor(acronym, issn)
    extractor.extract()
    journal = extractor.save()
    return journal.id


def task_extract_all_journals(acronym, issns):
    for issn in issns:
        job = q.enqueue(task_extract_journal, collection_acronym, issn)


# ISSSUES:


def task_extract_issue(acronym, issue_id):
    extractor = IssueExtactor(acronym, issue_id)
    extractor.extract()
    issue = extractor.save()
    return issue.id


def task_extract_all_issues(acronym, issns):
    for issn in issns:
        job = q.enqueue(task_extract_issue, collection_acronym, issn)


# ARTICLES:


def task_extract_article(acronym, article_id):
    extractor = ArticleExtactor(acronym, article_id)
    extractor.extract()
    article = extractor.save()
    return article.id


def task_extract_all_articles(acronym, issns):
    for issn in issns:
        job = q.enqueue(task_extract_article, collection_acronym, issn)
