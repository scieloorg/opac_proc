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
        'process_start_at': None,
        'process_finish_at': None,
        'process_completed': True,
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
                super(FooExtractor, self).__init__()
                # seu codigo aqui ...

            @update_metadata   <---- IMPORANTE !!!
            def extract(self):
                super(FooExtractor, self).extract()
                # seu codigo aqui ...

            def save(self):
                # implmementar só se for algo deferente

        """
        # Deve implementar a extração na subclase,
        # invocando este metodo como mostra a docstring
        raise NotImplemented

    def save(self):
        """
        Salva os dados coletados no datastore (mongo)
        """
        if self.metadata['is_locked']:
            msg = u"atributos metadata['is_locked'] indica que o processamento não finalizou corretamente."
            logger.error(msg)
            raise Exception(msg)
        elif self.model_class is None or self.model_name is None:
            msg = u"atributos model_class ou model_name não forma definidos na subclasse"
            logger.error(msg)
            raise Exception(msg)
        elif self.metadata['process_start_at'] is None:
            msg = u"não foi definida o timestamp de inicio, você definiu/invocou o metodo: extract() na subclasse?"
            logger.error(msg)
            raise Exception(msg)
        elif not self._raw_data:
            msg = u"os dados coletados estão vazios, você definiu/invocou o metodo: extract() na subclasse?"
            logger.error(msg)
            raise Exception(msg)
        elif not isinstance(self._raw_data, dict):
            msg = u"os dados extraidos, não são do tipo esperado: dict()"
            logger.error(msg)
            raise Exception(msg)
        else:
            # atualizamos as datas no self.metadata
            self._raw_data.update(**self.metadata)
            # salvamos no mongo
            try:
                obj = self.model_class(**self._raw_data)
                obj.save()
                return obj
            except Exception, e:
                msg = u"Não foi possível salvar %s. Exeção: %s" % (
                    self.model_name, e.message)
                logger.error(msg)
                raise Exception(msg)
