# coding: utf-8
from __future__ import unicode_literals

import logging

from opac_proc.extractors.ex_journals import JournalExtactor
from opac_proc.extractors.ex_issues import IssueExtactor
from opac_proc.extractors.ex_articles import ArticleExtactor


logger = logging.getLogger(__name__)


# Journals:

def task_extract_journal(acronym, issn):
    extractor = JournalExtactor(acronym, issn)
    extractor.extract()
    journal = extractor.save()
    return journal.id


# Issues:


def task_extract_issue(acronym, issue_id):
    extractor = IssueExtactor(acronym, issue_id)
    extractor.extract()
    issue = extractor.save()
    return issue.id


# Articles:


def task_extract_article(acronym, article_id):
    extractor = ArticleExtactor(acronym, article_id)
    extractor.extract()
    article = extractor.save()
    return article.id
