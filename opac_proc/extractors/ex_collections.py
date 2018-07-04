# coding: utf-8
import requests
from datetime import datetime
from opac_proc.datastore.models import ExtractCollection
from opac_proc.datastore.identifiers_models import CollectionIdModel
from opac_proc.extractors.base import BaseExtractor
from opac_proc.extractors.decorators import update_metadata

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "extract")
else:
    logger = getMongoLogger(__name__, "INFO", "extract")

PUBLICATION_SIZE_ENDPOINT = 'ajx/publication/size'


class CollectionExtractor(BaseExtractor):
    acronym = None

    extract_model_class = ExtractCollection
    ids_model_class = CollectionIdModel
    ids_model_name = 'CollectionIdModel'

    def __init__(self):
        super(CollectionExtractor, self).__init__()
        self.acronym = config.OPAC_PROC_COLLECTION
        self.get_instance_query = {
            'acronym': self.acronym
        }
        self.get_identifier_query = {
            'collection_acronym': self.acronym
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
        params['field'] = 'issn'
        url = '{0}/{1}'.format(config.OPAC_METRICS_URL, PUBLICATION_SIZE_ENDPOINT)
        journals = self._get_json_metrics('jornals', url, params)

        metrics = {
            'total_citation': int(references.get('total', 0)),
            'total_article': int(articles.get('total', 0)),
            'total_issue': int(issues.get('total', 0)),
            'total_journal': int(journals.get('total', 0)),
        }
        return metrics

    @update_metadata
    def extract(self):
        """
        Conecta com a fonte (AM) e extrai todos os dados (coleção).
        """
        logger.info(u'Inicia CollectionExtractor.extract(%s) %s' % (
            self.acronym, datetime.now()))

        for col in self.articlemeta.get_collections():
            if col['acronym'] == self.acronym:
                logger.info(u"Adicionado a coleção: %s" % self.acronym)
                self._raw_data = col
                break

        if not self._raw_data:
            msg = u"Não foi possível recuperar a Coleção (acronym: %s). A informação é vazía" % self.acronym
            logger.error(msg)
            raise Exception(msg)

        logger.info(u'Extração de ISSNs da coleção: %s - %s' % (self.acronym, datetime.now()))
        # extração de metricas
        if self._raw_data['has_analytics']:
            self._raw_data['metrics'] = self._extract_metrics()

        logger.info(u'Fim CollectionExtractor.extract(%s) %s' % (
            self.acronym, datetime.now()))
