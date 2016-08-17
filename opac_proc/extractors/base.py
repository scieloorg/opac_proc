# coding: utf-8
import logging
from datetime import datetime

import config
from opac_proc.extractors.source_clients.thrift import am_clients
from opac_proc.datastore.mongodb_connector import get_db_connection


logger = logging.getLogger(__name__)


class BaseExtractor(object):
    _db = None
    articlemeta = None

    _raw_data = {}      # definir no extract() da sublcasse
    model_class = None  # definir no __init__ da sublcasse
    model_name = ''     # definir no __init__ da sublcasse

    metadata = {
        'extraction_start_time': None,
        'extraction_finish_at': None,
        'extraction_complete': False,
    }

    def __init__(self):
        self._db = get_db_connection()
        self.articlemeta = am_clients.ArticleMeta(
            config.ARTICLE_META_THRIFT_DOMAIN,
            config.ARTICLE_META_THRIFT_PORT)

    def extract(self):
        """
        Conecta com a fonte (AM) e extrai todos os dados.

        Redefinir na subclasse:
        class FooExtractor(BaseExtractor):
            model_class = Foo
            model_name = 'foo'

            def __init__(self, args, kwargs):
                # seu codigo aqui ...

            def extract(self):
                super(FooExtractor, self).extract()
                # seu codigo aqui ...

            def save(self):
                # implmementar só se for algo deferente

        """
        self.metadata['extraction_start_time'] = datetime.now()
        # Deve implementar a extração na subclase,
        # invocando este metodo como mostra a docstring

    def save(self):
        """"
        Salva os dados coletados no datastore (mongo)
        """
        if not self.model_class or not self.model_name:
            msg = u"atributos model_class ou model_name não forma definidos na subclasse"
            logger.error(msg)
            raise Exception(msg)
        elif not self._raw_data:
            msg = u"os dados coletados estão vazios, você definiu/invocou o metodo: extract()? na subclasse?"
            logger.error(msg)
            raise Exception(msg)
        elif not isinstance(self._raw_data, dict):
            msg = u"os dados extraidos, não são do tipo esperado: dict()"
            logger.error(msg)
            raise Exception(msg)
        else:
            # atualizamos as datas no self.metadata
            self.metadata['extraction_finish_at'] = datetime.now()
            self.metadata['extraction_complete'] = True
            self._raw_data.update(**self.metadata)
            # salvamos no mongo
            try:
                obj = self.model_class(**self._raw_data)
                obj.save()
                return obj
            except Exception, e:
                msg = u"Não foi possível salvar %s. Exeção: %s" % (
                    self.model_name, e.messaage)
                logger.error(msg)
                raise Exception(msg)
