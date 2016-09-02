# coding: utf-8
import json
import logging
from datetime import datetime

import config
from opac_proc.extractors.source_clients.thrift import am_clients
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.extractors.decorators import update_metadata


logger = logging.getLogger(__name__)


class BaseTransformer(object):
    _db = None                          # definir no __init__ da sublcasse

    extract_model_class = None          # definir no __init__ da sublcasse
    extract_model_name = ''             # definir no __init__ da sublcasse
    extract_model_instance = None       # definir no __init__ da sublcasse

    transform_model_class = None        # definir no __init__ da sublcasse
    transform_model_name = ''           # definir no __init__ da sublcasse
    transform_model_instance = None     # definir no __init__ da sublcasse

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
            raise ValueError('subclase deve definir atributo: extract_model_class!')
        elif not self.extract_model_name:
            raise ValueError('subclase deve definir atributo: extract_model_name!')
        elif not self.transform_model_class:
            raise ValueError('subclase deve definir atributo: transform_model_class!')
        elif not self.transform_model_name:
            raise ValueError('subclase deve definir atributo: transform_model_name!')

        try:
            self.extract_model_instance = self.get_extract_model_instance(
                extract_model_key)
        except NotImplemented:
            raise ValueError('subclase deve definir o método: get_extract_model_instance!')
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
        obj_json = self.extract_model_instance.to_json()
        obj_dict = json.loads(obj_json)
        result_dict = {}
        for k, v in obj_dict.iteritems():
            if k not in self.exclude_fields:
                result_dict[k] = v
        return result_dict

    def get_extract_model_instance(self, key):
        raise NotImplemented

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
                # implmementar só se for algo deferente

        """
        raise NotImplemented
        # Deve implementar a extração na subclase,
        # invocando este metodo como mostra a docstring

    def save(self):
        """
        Salva os dados transformados no datastore (mongo)
        """

        try:
            self.transform_model_instance.save()
            self.transform_model_instance.update(**self.metadata)
            self.transform_model_instance.reload()
            return self.transform_model_instance
        except Exception, e:
            msg = u"Não foi possível salvar %s. Exeção: %s" % (
                self.transform_model_name, e)
            print msg
            logger.error(msg)
            raise Exception(msg)
