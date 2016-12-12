# coding: utf-8
import os
import thriftpy
import json
import logging
from datetime import date

from thriftpy.rpc import make_client
from xylose.scielodocument import Article, Journal, Issue

LIMIT = 1000

logger = logging.getLogger(__name__)


articlemeta_thrift = thriftpy.load(
    os.path.join(os.path.dirname(__file__))+'/articlemeta.thrift')


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

    def journals(self, collection=None, issn=None):
        offset = 0
        while True:
            identifiers = self.client.get_journal_identifiers(collection=collection, issn=issn, limit=LIMIT, offset=offset)
            if len(identifiers) == 0:
                raise StopIteration

            for identifier in identifiers:

                journal = self.client.get_journal(
                    code=identifier.code, collection=identifier.collection)

                jjournal = json.loads(journal)

                xjournal = Journal(jjournal)

                logger.info(u'Journal loaded: %s_%s' % (identifier.collection, identifier.code))

                yield xjournal

            offset += 1000

    def get_journal(self, code, collection=None):
        try:
            journal = self.client.get_journal(code=code, collection=collection)

            jjournal = json.loads(journal)

            xjournal = Journal(jjournal)

            logger.info(u'Journal loaded: %s_%s' % (collection, code))

            return xjournal

        except:
            msg = u'Error retrieving journal: %s_%s' % (collection, code)
            # raise ServerError(msg)
            logger.error(msg)
            pass

    def exists_article(self, code, collection):
        try:
            return self.client.exists_article(
                code,
                collection
            )
        except:
            msg = u'Error checking if document exists: %s_%s' % (collection, code)
            # raise ServerError(msg)
            logger.error(msg)
            pass

    def set_doaj_id(self, code, collection, doaj_id):
        try:
            article = self.client.set_doaj_id(
                code,
                collection,
                doaj_id
            )
        except:
            msg = u'Error senting doaj id for document: %s_%s' % (collection, code)
            # raise ServerError(msg)
            logger.error(msg)
            pass

    def document(self, code, collection, replace_journal_metadata=True, fmt='xylose'):
        try:
            article = self.client.get_article(
                code=code,
                collection=collection,
                replace_journal_metadata=True,
                fmt=fmt
            )
        except:
            msg = u'Error retrieving document: %s_%s' % (collection, code)
            # raise ServerError(msg)
            logger.error(msg)
            pass

        jarticle = None
        try:
            jarticle = json.loads(article)
        except:
            msg = u'Fail to load JSON when retrienving document: %s_%s' % (collection, code)
            raise ServerError(msg)

        if not jarticle:
            logger.warning(u'Document not found for : %s_%s' % (collection, code))
            return None

        if fmt == 'xylose':
            xarticle = Article(jarticle)
            logger.info(u'Document loaded: %s_%s' % (collection, code))
            return xarticle
        else:
            logger.info(u'Document loaded: %s_%s' % (collection, code))
            return article

    def documents(self, collection=None, issn=None, from_date=None,
                  until_date=None, fmt='xylose'):
        offset = 0
        while True:
            identifiers = self.client.get_article_identifiers(
                collection=collection, issn=issn, from_date=from_date,
                until_date=until_date, limit=LIMIT, offset=offset)

            if len(identifiers) == 0:
                raise StopIteration

            for identifier in identifiers:

                document = self.document(
                    code=identifier.code,
                    collection=identifier.collection,
                    replace_journal_metadata=True,
                    fmt=fmt
                )

                yield document

            offset += 1000

    def collections(self):

        return [i for i in self.client.get_collection_identifiers()]

    def issues(self, collection=None, issn=None, from_date=None, until_date=None):

        offset = 0

        while True:
            identifiers = self.client.get_issue_identifiers(
                collection=collection, issn=issn, from_date=from_date,
                until_date=until_date, limit=LIMIT, offset=offset)

            if len(identifiers) == 0:
                raise StopIteration

            for identifier in identifiers:
                try:
                    issue = self.client.get_issue(
                        code=identifier.code,
                        collection=identifier.collection,
                        replace_journal_metadata=True,
                    )

                    yield Issue(json.loads(issue))

                except:
                    msg = u'Error retrieving issue: %s_%s' % (collection, identifier)
                    # raise ServerError(msg)
                    logger.error(msg)
                    pass

            offset += 1000

    def get_issue(self, code, collection=None):
        try:
            issue = self.client.get_issue(
                code=code,
                collection=collection,
                replace_journal_metadata=True,
            )

            return Issue(json.loads(issue))

        except:
            msg = u'Error retrieving issue: %s_%s' % (collection, identifier)
            # raise ServerError(msg)
            logger.error(msg)
            pass

    def articles(self, collection=None, issn=None, from_date=None, until_date=None):

        offset = 0

        while True:
            identifiers = self.client.get_article_identifiers(
                collection=collection, issn=issn, from_date=from_date,
                until_date=until_date, limit=LIMIT, offset=offset)

            if len(identifiers) == 0:
                raise StopIteration

            for identifier in identifiers:
                try:
                    article = self.client.get_article(
                        code=identifier.code,
                        collection=identifier.collection,
                        replace_journal_metadata=True,
                    )

                    yield Article(json.loads(article))

                except:
                    msg = u'Error retrieving issue: %s_%s' % (collection, identifier)
                    # raise ServerError(msg)
                    logger.error(msg)
                    pass

            offset += 1000
