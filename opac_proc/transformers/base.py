# coding: utf-8
import os
import sys
import json

from opac_proc.datastore.mongodb_connector import get_db_connection

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "transform")
else:
    logger = getMongoLogger(__name__, "INFO", "transform")


class BaseTransformer(object):
    _db = None

    extract_model_class = None          # definir no __init__ da sublcasse
    extract_model_name = ''
    extract_model_instance = None

    transform_model_class = None        # definir no __init__ da sublcasse
    transform_model_name = ''
    transform_model_instance = None

    metadata = {
        'process_start_at': None,
        'process_finish_at': None,
        'process_completed': True,
    }

    exclude_fields = [
        '_id',
        'uuid',
        'updated_at',
        'is_locked',
        'is_deleted',
        'process_start_at',
        'process_finish_at',
        'process_completed',
        'must_reprocess',
    ]

    def __init__(self, extract_model_key, transform_model_uuid=None):
        """
        - extract_model_key:
            id ou chave do modelo (extract) que queremos transformar
        - transform_model_id: [opcional]
            quando definido, deve ser o id do modelo transformado
            que queremos atualizar.
            quando não for definido, se buscará na base um modelos
            com o mesmo uuid, caso não encontrar se criará uma
            nova instância da clase: self.transform_model_class
        """
        self._db = get_db_connection()
        if not extract_model_key:
            raise ValueError('extract_model_key inválido!')
        elif not self.extract_model_class:
            raise ValueError('subclasse deve definir atributo: extract_model_class!')
        elif not self.transform_model_class:
            raise ValueError('subclasse deve definir atributo: transform_model_class!')

        self.extract_model_name = str(self.extract_model_class)
        self.transform_model_name = str(self.transform_model_class)

        try:
            self.extract_model_instance = self.get_extract_model_instance(
                extract_model_key)
        except NotImplementedError:
            raise ValueError('subclasse deve definir o método: get_extract_model_instance!')
        except Exception, e:
            raise e

        if transform_model_uuid:
            try:
                self.transform_model_instance = self.transform_model_class.objects.get(
                    uuid=transform_model_uuid)
            except Exception, e:
                raise ValueError('transform_model_uuid inválido!!')
        else:
            try:
                # procuramos pelo model de extração com o mesmo UUID
                extract_uuid = self.extract_model_instance.uuid
                self.transform_model_instance = self.transform_model_class.objects.get(
                    uuid=extract_uuid)
            except Exception, e:
                # não achamos, teremos que retornar uma instância nova do modelo
                self.transform_model_instance = self.transform_model_class()

    def clean_for_xylose(self):
        """
        Pega os registros de self.extract_model_instance,
        remove a lista de atributos definida na lista: self.exclude_fields
        definida em cada subclase, e retorna um dicionario pronto para criar
        um instância de documento xylose
        """
        logger.debug(u'iniciando clean_for_xylose')
        obj_json = self.extract_model_instance.to_json()
        obj_dict = json.loads(obj_json)
        result_dict = {}
        for k, v in obj_dict.iteritems():
            if k not in self.exclude_fields:
                result_dict[k] = v
        logger.debug(u'finalizado clean_for_xylose')
        return result_dict

    def get_extract_model_instance(self, key):
        raise NotImplementedError

    # @update_metadata
    def transform(self):
        """
        Obtem o modelo extraido e aplica as tranformações necessárias
        para pode ser salvo no banco

        Redefinir na subclasse:
        class FooTransformer(BaseTransformer):
            extract_model_class = ExFoo
            extract_model_name = 'ex_foo'

            transform_model_class = TrFoo
            transform_model_name = 'tr_foo'

            def __init__(self, args, kwargs):
                # seu codigo aqui ...
                super(FooTransformer, self).__init__()
            @update_metadata
            def transform(self):
                super(FooTransformer, self).transform()
                # seu codigo aqui ...

            def save(self):
                # implmementar só se for algo diferente
        """
        raise NotImplementedError

    def save(self):
        """
        Salva os dados transformados no datastore (mongo)
        """
        logger.debug(u"iniciando save()")
        try:
            self.transform_model_instance.save()
            self.metadata['must_reprocess'] = False
            self.transform_model_instance.update(**self.metadata)
            self.transform_model_instance.reload()
        except Exception, e:
            msg = u"Não foi possível salvar %s. Exeção: %s" % (
                self.transform_model_name, e)
            logger.error(msg)
            raise Exception(msg)
        else:
            logger.debug(u"finalizando save()")
            return self.transform_model_instance
