from articlemeta.client import ThriftClient
from prometheus_client import Summary


AMAPI_THRIFT_GET_ARTICLE_REQUEST_TIME = Summary(
    'amapi_thirft_get_article_request_processing_seconds',
    'AM API THRIFT Time spent processing request'
)


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

    @AMAPI_THRIFT_GET_ARTICLE_REQUEST_TIME.time()
    def get_article(self, code, collection, fmt='opac', body=True):
        article = self.client.document(code=code, collection=collection, fmt=fmt, body=body)
        # gambe para o article.code
        result = article.data
        result['code'] = article.data['article']['code']
        result['collection'] = article.data['article']['collection']
        return result

    def collections(self):
        raise NotImplementedError
