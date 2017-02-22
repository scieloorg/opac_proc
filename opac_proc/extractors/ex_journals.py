# coding: utf-8
from datetime import datetime
from opac_proc.datastore.models import ExtractJournal
from opac_proc.extractors.base import BaseExtractor
from opac_proc.extractors.decorators import update_metadata

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger
from scieloh5m5 import h5m5

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "extract")
else:
    logger = getMongoLogger(__name__, "INFO", "extract")

PUBLICATION_SIZE_ENDPOINT = 'ajx/publication/size'


class JournalExtactor(BaseExtractor):
    acronym = None
    issn = None

    extract_model_class = ExtractJournal

    def __init__(self, acronym, issn):
        super(JournalExtactor, self).__init__()
        self.acronym = acronym
        self.issn = issn
        self.get_instance_query = {
            'code': self.issn
        }

    def _extract_metrics(self):
        logger.debug(u"iniciando: _extract_metrics")
        metrics_data = {
            'total_h5_index': 0,
            'total_h5_median': 0,
        }
        year = datetime.now().year
        _h5m5 = h5m5.get(self.issn, str(year))

        if _h5m5:
            metrics_data = {
                'total_h5_index': _h5m5['h5'],
                'total_h5_median': _h5m5['m5'],
            }
        return metrics_data

    @update_metadata
    def extract(self):
        """
        Conecta com a fonte (AM) e extrai todos os dados (coleção).
        """
        logger.info(u'Inicia JournalExtactor.extract(%s) %s' % (
            self.acronym, datetime.now()))

        journal = self.articlemeta.get_journal(collection=self.acronym, code=self.issn)
        self._raw_data = journal

        if not self._raw_data:
            msg = u"Não foi possível recuperar o Periódico (issn: %s, acronym: %s). A informação é vazía" % (
                self.issn, self.acronym)
            logger.error(msg)
            raise Exception(msg)

        # extração de métricas:
        self._raw_data['metrics'] = self._extract_metrics()

        logger.info(u'Fim JournalExtactor.extract(%s) %s', self.acronym, datetime.now())
