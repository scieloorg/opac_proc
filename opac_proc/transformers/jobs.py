# coding: utf-8
from opac_proc.transformers.tr_collections import CollectionTransformer
from opac_proc.transformers.tr_journals import JournalTransformer
from opac_proc.transformers.tr_issues import IssueTransformer
from opac_proc.transformers.tr_articles import ArticleTransformer

# Collections:


def task_transform_collection(acronym):
    ctr = CollectionTransformer(extract_model_key=acronym)
    ctr.transform()
    collection = ctr.save()
    return collection.id


# Journals:


def task_transform_journal(issn):
    jtr = JournalTransformer(extract_model_key=issn)
    jtr.transform()
    journal = jtr.save()
    return journal.id


# Issues:


def task_transform_issue(issue_id):
    itr = IssueTransformer(extract_model_key=issue_id)
    itr.transform()
    issue = itr.save()
    return issue.id


# Articles:


def task_transform_article(article_id):
    atr = ArticleTransformer(extract_model_key=article_id)
    atr.transform()
    article = atr.save()
    return article.id
