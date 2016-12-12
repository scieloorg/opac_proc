# coding: utf-8

import os
import thriftpy
import json
import logging
from datetime import date

from thriftpy.rpc import make_client
# from xylose.scielodocument import Article, Journal, Issue

LIMIT = 1000

logger = logging.getLogger(__name__)


articlemeta_thrift = thriftpy.load(
    os.path.join(os.path.dirname(__file__)) + '/articlemeta.thrift')


class ServerError(Exception):
    def __init__(self, message=None):
        self.message = message or 'thirftclient: ServerError'

    def __str__(self):
        return repr(self.message)


class ArticleMeta(object):

    def __init__(self, address, port):
        """
        Cliente thrift para o Articlemeta.
        """
        self._address = address
        self._port = port

    @property
    def client(self):

        client = make_client(
            articlemeta_thrift.ArticleMeta,
            self._address,
            self._port
        )
        return client

    def get_journal_identifiers(self, collection=None, issn=None, from_date=None, until_date=None):
        offset = 0
        while True:
            identifiers = self.client.get_journal_identifiers(collection=collection, issn=issn, limit=LIMIT, offset=offset)
            if len(identifiers) == 0:
                raise StopIteration

            for identifier in identifiers:
                yield identifier.code

            offset += 1000

    def get_issues_identifiers(self, collection=None, issn=None, from_date=None, until_date=None):
        offset = 0
        while True:
            identifiers = self.client.get_issue_identifiers(
                collection=collection, issn=issn, from_date=from_date,
                until_date=until_date, limit=LIMIT, offset=offset)

            if len(identifiers) == 0:
                raise StopIteration

            for identifier in identifiers:
                yield identifier.code

            offset += 1000

    def get_article_identifiers(self, collection=None, issn=None, from_date=None, until_date=None):
        offset = 0
        while True:
            identifiers = self.client.get_article_identifiers(
                collection=collection, issn=issn, from_date=from_date,
                until_date=until_date, limit=LIMIT, offset=offset)

            if len(identifiers) == 0:
                raise StopIteration

            for identifier in identifiers:
                yield identifier.code

            offset += 1000

    def get_journal(self, code, collection):
        try:
            journal = self.client.get_journal(
                code=code,
                collection=collection)
        except Exception, e:
            msg = 'Error retrieving journal: %s_%s. Exception: %s' % (
                collection, code, str(e))
            logger.error(msg)
            raise ServerError(msg)
        else:
            jjournal = None
            try:
                jjournal = json.loads(journal)
                logger.info('Journal loaded: %s_%s' % (collection, code))
            except Exception, e:
                msg = 'Fail to load JSON when retrienving Journal: %s_%s. Exception: %s' % (
                    collection, code, str(e))
                logger.error(msg)
                raise Exception(msg)
            else:
                return jjournal

    def get_issue(self, code, collection):
        try:
            issue = self.client.get_issue(
                code=code,
                collection=collection,
                replace_journal_metadata=True)
        except Exception, e:
            msg = 'Error retrieving Issue: %s_%s. Exception: %s' % (
                collection, code, str(e))
            logger.error(msg)
            raise ServerError(msg)
        else:
            jissue = None
            try:
                jissue = json.loads(issue)
                logger.info('Issue loaded: %s_%s' % (collection, code))
            except Exception, e:
                msg = 'Fail to load JSON when retrienving Issue: %s_%s. Exception: %s' % (
                    collection, code, str(e))
                logger.error(msg)
                raise Exception(msg)
            else:
                return jissue

    def get_article(self, code, collection):
        try:
            article = self.client.get_article(
                code=code,
                collection=collection,
                replace_journal_metadata=True,
                fmt='xylose')
        except Exception, e:
            msg = 'Error retrieving Article: %s_%s. Exception: %s' % (
                collection, code, str(e))
            logger.error(msg)
            raise ServerError(msg)
        else:
            jarticle = None
            try:
                jarticle = json.loads(article)
            except Exception, e:
                msg = 'Fail to load JSON when retrienving Article: %s_%s. Exception: %s' % (
                    collection, code, str(e))
                logger.error(msg)
                raise Exception(msg)
            else:
                return jarticle

    def collections(self):
        try:
            collections_list = []
            for collection in self.client.get_collection_identifiers():
                collections_list.append({
                    'code': collection.code,
                    'name': collection.name,
                    'acronym': collection.acronym,
                })
            return collections_list
        except Exception, e:
            msg = 'Error retrieving Collections. Exception: %s' % (e)
            logger.error(msg)
            raise ServerError(msg)
        # return [i for i in self.client.get_collection_identifiers()]
