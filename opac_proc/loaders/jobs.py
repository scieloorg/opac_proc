# coding: utf-8

from opac_proc.loaders.lo_collections import CollectionLoader
from opac_proc.loaders.lo_journals import JournalLoader
from opac_proc.loaders.lo_issues import IssueLoader
from opac_proc.loaders.lo_articles import ArticleLoader

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "load")
else:
    logger = getMongoLogger(__name__, "INFO", "load")


# Collections:


def task_load_collection(uuid):
    logger.debug('inciando: task_load_collection(%s)' % uuid)
    logger.debug('instanciando CollectionLoader(%s)' % uuid)
    c_loader = CollectionLoader(uuid)
    logger.debug('chamando CollectionLoader(%s).prepare()' % uuid)
    c_loader.prepare()
    logger.debug('chamando CollectionLoader(%s).load' % uuid)
    c_loader.load()
    logger.debug('fim: task_load_collection(%s)' % uuid)


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
