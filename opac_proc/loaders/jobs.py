# coding: utf-8
from __future__ import unicode_literals

import logging

from opac_proc.loaders.lo_collections import CollectionLoader
from opac_proc.loaders.lo_journals import JournalLoader
from opac_proc.loaders.lo_issues import IssueLoader
from opac_proc.loaders.lo_articles import ArticleLoader

# Collections:


def task_load_collection(uuid):
    c_loader = CollectionLoader(uuid)
    c_loader.prepare()
    c_loader.load()


# Journals:


def task_load_journal(uuid):
    j_loader = JournalLoader(uuid)
    j_loader.prepare()
    j_loader.load()


# Issues:


def task_load_issue(uuid):
    i_loader = IssueLoader(uuid)
    i_loader.prepare()
    i_loader.load()


# Articles:


def task_load_article(uuid):
    a_loader = ArticleLoader(uuid)
    a_loader.prepare()
    a_loader.load()
