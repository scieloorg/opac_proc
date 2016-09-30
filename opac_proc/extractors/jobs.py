# coding: utf-8
from opac_proc.extractors.ex_collections import CollectionExtactor
from opac_proc.extractors.ex_journals import JournalExtactor
from opac_proc.extractors.ex_issues import IssueExtactor
from opac_proc.extractors.ex_articles import ArticleExtactor


# Collection:

def task_extract_collection(acronym):
    extractor = CollectionExtactor(acronym)
    extractor.extract()
    collection = extractor.save()


# Journals:

def task_extract_journal(acronym, issn):
    extractor = JournalExtactor(acronym, issn)
    extractor.extract()
    journal = extractor.save()


# Issues:


def task_extract_issue(acronym, issue_id):
    extractor = IssueExtactor(acronym, issue_id)
    extractor.extract()
    issue = extractor.save()


# Articles:


def task_extract_article(acronym, article_id):
    extractor = ArticleExtactor(acronym, article_id)
    extractor.extract()
    article = extractor.save()
