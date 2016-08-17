# coding: utf-8
import logging
from datetime import datetime

from opac_proc.datastore.extract.models import ExtractCollection
from opac_proc.extractors.base import BaseExtractor


logger = logging.getLogger(__name__)


class ColectionExtactor(BaseExtractor):
    acronym = None
    children_ids = []

    model_class = ExtractCollection
    model_name = 'ExtractCollection'

    def __init__(self, acronym):
        super(ColectionExtactor, self).__init__()
        self.acronym = acronym

    def extract(self):
        """
        Conecta com a fonte (AM) e extrai todos os dados (coleção).
        """
        super(ColectionExtactor, self).extract()
        logger.info(u'Inicia ColectionExtactor.extract(%s) %s' % (self.acronym, datetime.now()))

        cols = self.articlemeta.collections()
        for col in cols:
            if col['acronym'] == self.acronym:
                logger.info(u"Adicionado a coleção: %s" % self.acronym)
                print u"Adicionado a coleção: %s" % self.acronym
                self._raw_data = col
                break

        if not self._raw_data:
            msg = u"Não foi possível recuperar a Coleção (acronym: %s). A informação é vazía" % self.acronym
            logger.error(msg)
            raise Exception(msg)

        logger.info(u'Extração de ISSNs da coleção: %s - %s' % (self.acronym, datetime.now()))
        # recuperamos os identificadores ISSNs
        journals_ids = self.articlemeta.get_journal_identifiers(collection=self.acronym)
        for issn in journals_ids:
            issues_ids = self.articlemeta.get_issues_identifiers(collection=self.acronym, issn=issn)
            articles_ids = self.articlemeta.get_article_identifiers(collection=self.acronym, issn=issn)

            self.children_ids.append({
                'issn': issn,
                'issues_ids': [id for id in issues_ids],
                'articles_ids': [id for id in articles_ids],
            })

        logger.info(u'Extraidos %s ISSNs da coleção: %s - %s' % (len(self.children_ids), self.acronym, datetime.now()))

        if not self.children_ids:
            msg = u"Não foi possível recuperar os ISSNs da Coleção (acronym: %s). A informação é vazía" % self.acronym
            logger.error(msg)
            raise Exception(msg)
        else:
            # atualizo self.metadata para que self.children_ids seja salvo junto com self.raw_data no save()
            self.metadata['children_ids'] = self.children_ids
        logger.info(u'Fim ColectionExtactor.extract(%s) %s' % (self.acronym, datetime.now()))
