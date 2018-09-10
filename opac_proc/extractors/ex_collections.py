# coding: utf-8
import requests
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

PUBLICATION_SIZE_ENDPOINT = 'ajx/publication/size'
ARTICLE_META_COLLECTION_ENDPOINT = 'api/v1/collection/'


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

    def _get_json_metrics(self, metric_name, url, params):
        json_data = {}

        try:
            response = requests.get(url, params=params)
        except Exception, e:
            logger.error(u'Erro recuperando as metricas: %s (url=%s, msg=%s)' % (metric_name, url, str(e)))
        else:
            if response.status_code == 200:
                json_data = response.json()
        return json_data

    def _extract_metrics(self):
        params = {
            'code': self.acronym,
            'collection': self.acronym,
        }
        # references:
        url = '{0}/{1}'.format(config.OPAC_METRICS_URL, PUBLICATION_SIZE_ENDPOINT)
        params['field'] = 'citations'
        references = self._get_json_metrics('references', url, params)

        # articles:
        url = '{0}/{1}'.format(config.OPAC_METRICS_URL, PUBLICATION_SIZE_ENDPOINT)
        params['field'] = 'documents'
        articles = self._get_json_metrics('articles', url, params)

        # issues:
        params['field'] = 'issue'
        url = '{0}/{1}'.format(config.OPAC_METRICS_URL, PUBLICATION_SIZE_ENDPOINT)
        issues = self._get_json_metrics('issues', url, params)

        # jornals:
        url = 'http://{0}:{1}/{2}'.format(config.ARTICLE_META_REST_DOMAIN,
                                          config.ARTICLE_META_REST_PORT,
                                          ARTICLE_META_COLLECTION_ENDPOINT)
        journals = self._get_json_metrics('journals', url, params)

        metrics = {
            'total_citation': int(references.get('total', 0)),
            'total_article': int(articles.get('total', 0)),
            'total_issue': int(issues.get('total', 0)),
            'total_journal': int(journals.get('journal_count', {}).get('current', 0))
        }
        return metrics

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

        # extração de metricas
        self._raw_data['metrics'] = self._extract_metrics()

        logger.info(u'Fim CollectionExtractor.extract(%s) %s' % (
            self.acronym, datetime.now()))
