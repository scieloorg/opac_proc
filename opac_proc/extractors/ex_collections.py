# coding: utf-8
from datetime import datetime
from opac_proc.datastore.models import ExtractCollection
from opac_proc.extractors.base import BaseExtractor
from opac_proc.extractors.decorators import update_metadata

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "extract")
else:
    logger = getMongoLogger(__name__, "INFO", "extract")


class CollectionExtractor(BaseExtractor):
    acronym = None
    children_ids = []

    extract_model_class = ExtractCollection

    def __init__(self, acronym):
        super(CollectionExtractor, self).__init__()
        self.acronym = acronym
        self.get_instance_query = {
            'acronym': self.acronym
        }

    @update_metadata
    def extract(self):
        """
        Conecta com a fonte (AM) e extrai todos os dados (coleção).
        """
        logger.info(u'Inicia CollectionExtractor.extract(%s) %s' % (
            self.acronym, datetime.now()))

        for col in self.articlemeta.collections():
            if col['acronym'] == self.acronym:
                logger.info(u"Adicionado a coleção: %s" % self.acronym)
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
        logger.info(u'Fim CollectionExtractor.extract(%s) %s' % (self.acronym, datetime.now()))
