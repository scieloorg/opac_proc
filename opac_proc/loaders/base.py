# coding: utf-8
import logging
import json
from datetime import datetime
from mongoengine.context_managers import switch_db
from opac_proc.datastore.mongodb_connector import (
    register_connections, get_opac_proc_db_name, get_opac_webapp_db_name)

logger = logging.getLogger(__name__)
OPAC_PROC_DB_NAME = get_opac_proc_db_name()
OPAC_WEBAPP_DB_NAME = get_opac_webapp_db_name()


class BaseLoader(object):
    transform_model_class = None        # definir no __init__ da sublcasse
    transform_model_name = ''
    transform_model_instance = None     # definir no __init__ da sublcasse

    opac_model_class = None
    opac_model_name = ''
    opac_model_instance = None

    load_model_class = None
    load_model_name = ''
    load_model_instance = None

    metadata = {
        'process_start_at': None,
        'process_finish_at': None,
        'process_completed': False,
    }

    fields_to_load = [
        # definir na subclase a lista de campos a incluir no load
    ]

    def __init__(self, transform_model_uuid):
        """
        - transform_model_uuid:
            uuid do modelo do TransformModel que queremos carregar
        """
        register_connections()
        if not transform_model_uuid:
            raise ValueError('transform_model_uuid inválido!')
        elif not self.transform_model_class:
            raise ValueError('subclasse deve definir atributo: transform_model_class!')
        elif not self.opac_model_class:
            raise ValueError('subclasse deve definir atributo: opac_model_class!')
        elif not self.load_model_class:
            raise ValueError('subclasse deve definir atributo: load_model_class!')

        self.transform_model_name = str(self.transform_model_class)
        self.opac_model_name = str(self.opac_model_class)
        self.load_model_name = str(self.load_model_class)

        self.get_transform_model_instance(
            query={'uuid': transform_model_uuid})

        # buscamos uma instância na base opac com o mesmo UUID
        uuid_str = str(transform_model_uuid).replace("-", "")
        self.get_opac_model_instance(
            query={'_id': uuid_str})

        # Load model instance: to track process times by uuid
        self.get_load_model_instance(
            query={'uuid': transform_model_uuid})

    def get_transform_model_instance(self, query={}):
        # retornamos uma instância do transform_model_class
        # correspondente com a **query dict.
        with switch_db(self.transform_model_class, OPAC_PROC_DB_NAME):
            self.transform_model_instance = self.transform_model_class.objects(
                **query).first()

    def get_opac_model_instance(self, query={}):
        # retornamos uma instância do opac_model_class
        # correspondente com a **query dict.
        with switch_db(self.opac_model_class, OPAC_WEBAPP_DB_NAME):
            self.opac_model_instance = self.opac_model_class.objects(
                **query).first()

    def get_load_model_instance(self, query={}):
        # retornamos uma instância do load_model_class
        # correspondente com a **query dict.
        with switch_db(self.load_model_class, OPAC_PROC_DB_NAME):
            self.load_model_instance = self.load_model_class.objects(
                **query).first()
            if not self.load_model_instance:
                self.load_model_instance = self.load_model_class()
                self.load_model_instance.uuid = query['uuid']
                self.load_model_instance.save()

    def transform_model_instance_to_python(self):
        """
        Recupera a instância de transform_model_class,
        removemos metadata e retornamos um dicionario (python) pronto
        para criar uma instância do opac_model_class
        """
        self.metadata['process_start_at'] = datetime.now()

        t_model = self.transform_model_instance
        if not t_model:
            raise ValueError("Precisa instanciar o self.transform_model_instance")

        result_dict = {}
        for field in self.fields_to_load:
            if field in ["jid", "iid", "aid"]:
                result_dict[field] = str(t_model.uuid).replace("-", "")
            elif hasattr(self, 'prepare_%s' % field):
                result_dict[field] = getattr(self, 'prepare_%s' % field)()
            elif hasattr(t_model, field):
                result_dict[field] = getattr(t_model, field)
        return result_dict

    def prepare(self):
        obj_dict = self.transform_model_instance_to_python()
        obj_dict['_id'] = str(self.transform_model_instance.uuid).replace("-", "")

        with switch_db(self.opac_model_class, OPAC_WEBAPP_DB_NAME):
            if self.opac_model_instance is None:
                self.opac_model_instance = self.opac_model_class(**obj_dict)
            else:
                for k, v in obj_dict.iteritems():
                    self.opac_model_instance[k] = v
        return self.opac_model_instance

    def load(self):
        with switch_db(self.opac_model_class, OPAC_WEBAPP_DB_NAME):
            self.opac_model_instance.save()

        with switch_db(self.load_model_class, OPAC_PROC_DB_NAME):
            self.metadata['process_finish_at'] = datetime.now()
            self.metadata['process_completed'] = True
            self.metadata['must_reprocess'] = False
            self.load_model_instance.update(**self.metadata)
