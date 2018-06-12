from articlemeta.client import ThriftClient
from opac_proc.core.prometheus_metrics import push_metric


class ArticleMeta(object):

    def __init__(self, address, port):
        """
        Cliente thrift para o Articlemeta.
        """
        self._address = address
        self._port = port
        self._domain = "%s:%s" % (self._address, self._port)

    @property
    def client(self):
        client = ThriftClient(domain=self._domain)
        return client

    def get_journal_identifiers(self, collection=None, issn=None, from_date=None, until_date=None):
        raise NotImplementedError

    def get_issues_identifiers(self, collection=None, issn=None, from_date=None, until_date=None):
        raise NotImplementedError

    def get_article_identifiers(self, collection=None, issn=None, from_date=None, until_date=None):
        raise NotImplementedError

    def get_journal(self, code, collection):
        raise NotImplementedError

    def get_issue(self, code, collection):
        raise NotImplementedError

    @push_metric('amapi_thirft_get_article_request_processing_seconds')
    def get_article(self, code, collection, fmt='opac', body=True):
        article = self.client.document(code=code, collection=collection, fmt=fmt, body=body)
        return article.data

    def collections(self):
        raise NotImplementedError
