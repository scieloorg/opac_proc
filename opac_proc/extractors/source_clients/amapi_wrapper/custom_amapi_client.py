from articlemeta.client import ThriftClient
from opac_proc.core.prometheus_metrics import push_metric
from opac_proc.web.config import ARTICLE_META_THRIFT_TIMEOUT


class ArticleMeta(object):

    def __init__(self, address, port, timeout=ARTICLE_META_THRIFT_TIMEOUT):
        """
        Cliente thrift para o Articlemeta.
        """
        self._address = address
        self._port = port
        self._domain = "%s:%s" % (self._address, self._port)
        self.timeout = timeout

    @property
    def client(self):
        client = ThriftClient(domain=self._domain, timeout=self.timeout)
        return client

    def get_collections_identifiers(self):
        objs = self.client.collections(only_identifiers=True)
        for obj in objs:
            yield obj.__dict__

    def get_journals_identifiers(self, collection=None, issn=None):
        objs = self.client.journals(collection=collection, issn=issn, only_identifiers=True)
        for obj in objs:
            yield obj.__dict__

    def get_issues_identifiers(self, collection=None, issn=None, from_date=None, until_date=None):
        objs = self.client.issues(
            collection=collection, issn=issn,
            from_date=from_date, until_date=until_date,
            only_identifiers=True)
        for obj in objs:
            yield obj.__dict__

    def get_articles_identifiers(self, collection=None, issn=None, from_date=None, until_date=None):
        objs = self.client.documents(
            collection=collection, issn=issn,
            from_date=from_date, until_date=until_date,
            only_identifiers=True)
        for obj in objs:
            yield obj.__dict__

    # methods to retrieve list of full docuements (not identifiers):

    def get_collections(self):
        objs = self.client.collections()
        for obj in objs:
            yield obj.__dict__

    def get_journals(self, collection=None, issn=None):
        objs = self.client.journals(collection=collection, issn=issn)
        for obj in objs:
            yield obj.__dict__

    def get_issues(self, collection=None, issn=None, from_date=None, until_date=None):
        objs = self.client.issues(
            collection=collection, issn=issn,
            from_date=from_date, until_date=until_date)
        for obj in objs:
            yield obj.__dict__

    def get_articles(self, collection=None, issn=None, from_date=None, until_date=None):
        objs = self.client.documents(
            collection=collection, issn=issn,
            from_date=from_date, until_date=until_date)
        for obj in objs:
            yield obj.__dict__

    # methods to retrieve list of full XYLOSE docuements (not identifiers):

    def get_xylose_collections(self):
        objs = self.client.collections()
        for obj in objs:
            yield obj

    def get_xylose_journals(self, collection=None, issn=None):
        objs = self.client.journals(collection=collection, issn=issn)
        for obj in objs:
            yield obj

    def get_xylose_issues(self, collection=None, issn=None, from_date=None, until_date=None):
        objs = self.client.issues(
            collection=collection, issn=issn,
            from_date=from_date, until_date=until_date)
        for obj in objs:
            yield obj

    def get_xylose_articles(self, collection=None, issn=None, from_date=None, until_date=None):
        objs = self.client.documents(
            collection=collection, issn=issn,
            from_date=from_date, until_date=until_date)
        for obj in objs:
            yield obj

    def get_journal(self, code, collection):
        """
        methods to get one single JOURNAL as dict()
        @params:
        - code: journal ISSN
        - collection: journal's collection ('spa', 'scl', etc)
        """
        journal = self.client.document(code=code, collection=collection)
        return journal.data

    def get_issue(self, code, collection):
        """
        methods to get one single ISSUE as dict()
        @params:
        - code: issue PID
        - collection: issue's collection ('spa', 'scl', etc)
        """
        issue = self.client.issue(code=code, collection=collection)
        return issue.data

    @push_metric('amapi_thirft_get_article_request_processing_seconds')
    def get_article(self, code, collection, fmt='opac', body=True):
        """
        methods to get one single ARTICLE as dict()
        @params:
        - code: article PID
        - collection: article's collection ('spa', 'scl', etc)
        - fmt: 'opac' reduce the reponse size to fit the OPAC processing needs
        - body: True/False to retrieve all article's body content or not
        """
        article = self.client.document(code=code, collection=collection, fmt=fmt, body=body)
        return article.data

    def get_xylose_journal(self, code, collection):
        """
        methods to get one single JOURNAL as xylose object
        @params:
        - code: journal ISSN
        - collection: journal's collection ('spa', 'scl', etc)
        """
        journal = self.client.journal(code=code, collection=collection)
        return journal

    def get_xylose_issue(self, code, collection):
        """
        methods to get one single ISSUE as xylose object
        @params:
        - code: issue PID
        - collection: issue's collection ('spa', 'scl', etc)
        """
        issue = self.client.issue(code=code, collection=collection)
        return issue

    @push_metric('amapi_thirft_get_article_request_processing_seconds')
    def get_xylose_article(self, code, collection, fmt='opac', body=True):
        """
        methods to get one single ARTICLE as xylose object
        @params:
        - code: article PID
        - collection: article's collection ('spa', 'scl', etc)
        - fmt: 'opac' reduce the reponse size to fit the OPAC processing needs
        - body: True/False to retrieve all article's body content or not
        """
        article = self.client.document(code=code, collection=collection, fmt=fmt, body=body)
        return article
