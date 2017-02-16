# coding: utf-8
from datetime import datetime

from opac_proc.datastore.models import ExtractArticle
from opac_proc.extractors.base import BaseExtractor
from opac_proc.extractors.decorators import update_metadata

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "extract")
else:
    logger = getMongoLogger(__name__, "INFO", "extract")


class ArticleExtractor(BaseExtractor):
    acronym = None
    article_id = None

    extract_model_class = ExtractArticle

    def __init__(self, acronym, article_id):
        super(ArticleExtractor, self).__init__()
        self.acronym = acronym
        self.article_id = article_id
        self.get_instance_query = {
            'code': self.article_id,
            'collection': self.acronym,
        }

    @update_metadata
    def extract(self):
        """
        Conecta com a fonte (AM) e extrai todos os dados (Article).
        """
        logger.info(u'Inicia ArticleExtractor.extract(%s) %s' % (
            self.acronym, datetime.now()))

        article = self.articlemeta.get_article(collection=self.acronym, code=self.article_id)
        self._raw_data = article

        if not self._raw_data:
            msg = u"Não foi possível recuperar a Article (acronym: %s). A informação é vazía" % self.acronym
            logger.error(msg)
            raise Exception(msg)

        logger.info(u'Fim ArticleExtractor.extract(%s) %s' % (
            self.acronym, datetime.now()))
