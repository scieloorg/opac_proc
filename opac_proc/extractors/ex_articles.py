# coding: utf-8

from opac_proc.extractors.source_clients.amapi_wrapper import custom_amapi_client
from opac_proc.datastore.models import ExtractArticle
from opac_proc.datastore.identifiers_models import ArticleIdModel
from opac_proc.extractors.base import BaseExtractor
from opac_proc.extractors.decorators import update_metadata
from opac_proc.core.prometheus_metrics import push_metric

from opac_proc.web import config


class ArticleExtractor(BaseExtractor):
    acronym = None
    article_id = None

    extract_model_class = ExtractArticle
    ids_model_class = ArticleIdModel
    ids_model_name = 'ArticleIdModel'

    def __init__(self, article_id):
        super(ArticleExtractor, self).__init__()
        self.acronym = config.OPAC_PROC_COLLECTION
        self.article_id = article_id
        self.get_instance_query = {
            'code': self.article_id,
            'collection': self.acronym,
        }
        self.get_identifier_query = {
            'article_pid': self.article_id
        }
        # redefinimos o cliente articlemeta para usar a api com: fmt='opac'
        self.articlemeta = custom_amapi_client.ArticleMeta(
            config.ARTICLE_META_THRIFT_DOMAIN,
            config.ARTICLE_META_THRIFT_PORT,
            config.ARTICLE_META_THRIFT_TIMEOUT)

    @push_metric('ex_articles_extract_method_processing_seconds')
    @update_metadata
    def extract(self):
        """
        Conecta com a fonte (AM) e extrai todos os dados (Article).
        """

        article = self.articlemeta.get_article(
            collection=self.acronym,
            code=self.article_id,
            fmt=config.ARTICLE_META_THRIFT_DEFAULT_ARTICLE_FMT,
            body=True)
        self._raw_data = article
        if not self._raw_data:
            msg = u"Não foi possível recuperar a Article (acronym: %s). A informação é vazía" % self.acronym
            raise RuntimeError(msg)
