# coding: utf-8
import logging
from datetime import datetime

from opac_proc.datastore.extract.models import ExtractArticle
from opac_proc.extractors.base import BaseExtractor
from opac_proc.extractors.decorators import update_metadata


logger = logging.getLogger(__name__)


class ArticleExtactor(BaseExtractor):
    acronym = None
    article_id = None

    model_class = ExtractArticle
    model_name = 'ExtractArticle'

    def __init__(self, acronym, article_id):
        super(ArticleExtactor, self).__init__()
        self.acronym = acronym
        self.article_id = article_id

    @update_metadata
    def extract(self):
        """
        Conecta com a fonte (AM) e extrai todos os dados (Article).
        """
        logger.info(u'Inicia ArticleExtactor.extract(%s) %s' % (
            self.acronym, datetime.now()))

        article = self.articlemeta.get_article(collection=self.acronym, code=self.article_id)
        self._raw_data = article

        if not self._raw_data:
            msg = u"Não foi possível recuperar a Article (acronym: %s). A informação é vazía" % self.acronym
            logger.error(msg)
            raise Exception(msg)

        logger.info(u'Fim ArticleExtactor.extract(%s) %s' % (
            self.acronym, datetime.now()))
