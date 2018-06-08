# coding: utf-8
from datetime import datetime

from opac_proc.extractors.source_clients.amapi_wrapper import custom_amapi_client
from opac_proc.datastore.models import ExtractArticle
from opac_proc.datastore.identifiers_models import ArticleIdModel
from opac_proc.extractors.base import BaseExtractor
from opac_proc.extractors.decorators import update_metadata
from prometheus_client import Summary

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "extract")
else:
    logger = getMongoLogger(__name__, "INFO", "extract")


EX_ARTICLES_EXTRACT_METHOD_PROCESSING = Summary(
    'ex_articles_extract_method_processing_seconds',
    'Time spent processing during execution of extract method (ex_articles)'
)


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
            config.ARTICLE_META_THRIFT_PORT)

    @EX_ARTICLES_EXTRACT_METHOD_PROCESSING.time()
    @update_metadata
    def extract(self):
        """
        Conecta com a fonte (AM) e extrai todos os dados (Article).
        """
        logger.info(u'Inicia ArticleExtractor.extract(%s) %s' % (
            self.acronym, datetime.now()))

        article = self.articlemeta.get_article(
            collection=self.acronym,
            code=self.article_id,
            fmt=config.ARTICLE_META_THRIFT_DEFAULT_ARTICLE_FMT,
            body=True)
        self._raw_data = article

        if not self._raw_data:
            msg = u"Não foi possível recuperar a Article (acronym: %s). A informação é vazía" % self.acronym
            logger.error(msg)
            raise Exception(msg)

        logger.info(u'Fim ArticleExtractor.extract(%s) %s' % (
            self.acronym, datetime.now()))
