# coding: utf-8
import requests

from opac_proc.datastore.models import (
    TransformCollection,
    LoadCollection)
from opac_proc.loaders.base import BaseLoader
from opac_schema.v1.models import Collection as OpacCollection
from opac_schema.v1.models import CollectionMetrics

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "load")
else:
    logger = getMongoLogger(__name__, "INFO", "load")

PUBLICATION_SIZE_ENDPOINT = 'ajx/publication/size'


class CollectionLoader(BaseLoader):
    transform_model_class = TransformCollection
    transform_model_instance = None

    opac_model_class = OpacCollection
    opac_model_instance = None

    load_model_class = LoadCollection
    load_model_instance = None

    fields_to_load = [
        'acronym',
        'name',
        'metrics',
    ]

    def _get_json_metrics(metric_name, url, params):
        json_data = {}

        try:
            response = requests.get(url, params=params)
        except Exception, e:
            logger.error(u'Erro recuperando as metricas: %s (url=%s, msg=%s)' % (metric_name, url, str(e)))
        else:
            if response.status_code == 200:
                json_data = response.json()
        return json_data

    def prepare_metrics(self):
        params = {
            'code': self.load_model_instance.acronym,
            'collection': self.load_model_instance.acronym,
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
        journals_url = '{0}/{1}'.format(config.OPAC_METRICS_URL, PUBLICATION_SIZE_ENDPOINT)
        journals = self._get_json_metrics('jornals', url, params)

        metrics = {}
        metrics['total_citation'] = int(references.get('total', 0))
        metrics['total_article'] = int(articles.get('total', 0))
        metrics['total_issue'] = int(issues.get('total', 0))
        metrics['total_journal'] = int(journals.get('total', 0))
        return metrics
