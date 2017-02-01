# coding: utf-8
import os
import sys
from datetime import datetime
from mongoengine.context_managers import switch_db
from opac_proc.datastore.mongodb_connector import (
    get_db_connection,
    register_connections,
    get_opac_proc_db_name,
    get_opac_webapp_db_name)

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "load")
else:
    logger = getMongoLogger(__name__, "INFO", "load")


OPAC_PROC_DB_NAME = get_opac_proc_db_name()
OPAC_WEBAPP_DB_NAME = get_opac_webapp_db_name()


class BaseLoader(object):
    _db = None
    transform_model_class = None        # definir no __init__ da sublcasse
    transform_model_name = ''
    transform_model_instance = None     # definir no __init__ da sublcasse

    opac_model_class = None             # definir no __init__ da sublcasse
    opac_model_name = ''
    opac_model_instance = None          # definir no __init__ da sublcasse

    load_model_class = None             # definir no __init__ da sublcasse
    load_model_name = ''
    load_model_instance = None          # definir no __init__ da sublcasse

    _uuid = None
    _uuid_str = None

    metadata = {
        'uuid': None,
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
        self._db = get_db_connection()
        register_connections()
        if not transform_model_uuid:
            raise ValueError(u'transform_model_uuid inválido!')
        elif not self.transform_model_class:
            raise ValueError(u'subclasse deve definir atributo: transform_model_class!')
        elif not self.opac_model_class:
            raise ValueError(u'subclasse deve definir atributo: opac_model_class!')
        elif not self.load_model_class:
            raise ValueError(u'subclasse deve definir atributo: load_model_class!')

        self.transform_model_name = str(self.transform_model_class)
        self.opac_model_name = str(self.opac_model_class)
        self.load_model_name = str(self.load_model_class)

        self._uuid = transform_model_uuid
        self._uuid_str = str(transform_model_uuid).replace("-", "")

        self.get_transform_model_instance(query_dict={'uuid': self._uuid})

        # buscamos uma instância na base opac com o mesmo UUID
        self.get_opac_model_instance(query_dict={'_id': self._uuid_str})

        # Load model instance: to track process times by uuid
        self.get_load_model_instance(query_dict={'uuid': self._uuid})

        self.metadata['uuid'] = self._uuid

    def get_transform_model_instance(self, query_dict):
        # recuperamos uma instância do transform_model_class
        # correspondente com a **query_dict dict.
        # caso não exista, levantamos uma exeção por não ter o dado fonte
        with switch_db(self.transform_model_class, OPAC_PROC_DB_NAME):
            logger.debug(u'recuperando modelo: %s' % self.transform_model_name)
            self.transform_model_instance = self.transform_model_class.objects(**query_dict).first()
            logger.debug(u'modelo %s encontrado. query_dict: %s' % (self.transform_model_name, query_dict))

    def get_opac_model_instance(self, query_dict):
        # recuperamos uma instância do opac_model_class
        # correspondente com a **query_dict dict.
        # caso não exista, retornamos uma nova instância
        with switch_db(self.opac_model_class, OPAC_WEBAPP_DB_NAME):
            try:
                logger.debug(u'recuperando modelo: %s' % self.opac_model_name)
                self.opac_model_instance = self.opac_model_class.objects.get(**query_dict)
                logger.debug(u'modelo %s encontrado. query_dict: %s' % (self.opac_model_name, query_dict))
            except self.opac_model_class.DoesNotExist:
                self.opac_model_instance = None
            except Exception as e:
                logger.error(e)
                raise e

    def get_load_model_instance(self, query_dict):
        # recuperamos uma instância do load_model_class
        # correspondente com a **query_dict dict.
        # caso não exista, retornamos uma nova instância
        with switch_db(self.load_model_class, OPAC_PROC_DB_NAME):
            try:
                logger.debug(u'recuperando modelo: %s' % self.load_model_name)
                self.load_model_instance = self.load_model_class.objects.get(**query_dict)
                logger.debug(u'modelo %s encontrado. query_dict: %s' % (self.load_model_name, query_dict))
            except self.load_model_class.DoesNotExist:
                logger.debug(u'load_model_instance não foi encontrado. criamos nova instância')
                self.load_model_instance = self.load_model_class(**query_dict)
                self.load_model_instance['uuid'] = self._uuid
                self.load_model_instance.save()
                self.load_model_instance.reload()
                logger.debug('nova instancia de load_model_instance. uuid: %s' % self.load_model_instance['uuid'])
            except Exception, e:
                logger.error(e)
                raise e

    def transform_model_instance_to_python(self):
        """
        Recupera a instância de transform_model_class,
        removemos metadata e retornamos um dicionario (python) pronto
        para criar uma instância do opac_model_class
        """
        logger.debug(u"iniciando metodo transform_model_instance_to_python (uuid: %s)" % self.metadata['uuid'])
        self.metadata['process_start_at'] = datetime.now()

        t_model = self.transform_model_instance
        if not t_model:
            raise ValueError(u"Precisa instanciar o transform_model_instance")

        result_dict = {}
        for field in self.fields_to_load:
            if field in ["jid", "iid", "aid"]:
                result_dict[field] = self._uuid_str
            elif hasattr(self, 'prepare_%s' % field):
                result_dict[field] = getattr(self, 'prepare_%s' % field)()
            elif hasattr(t_model, field):
                result_dict[field] = getattr(t_model, field)
        logger.debug(u"finalizando metodo transform_model_instance_to_python (uuid: %s)" % self.metadata['uuid'])
        return result_dict

    def prepare(self):
        logger.debug(u"iniciando metodo prepare (uuid: %s)" % self.metadata['uuid'])
        obj_dict = self.transform_model_instance_to_python()
        obj_dict['_id'] = self._uuid_str

        logger.debug(u"recuperando modelo no opac (_id: %s)" % obj_dict['_id'])
        with switch_db(self.opac_model_class, OPAC_WEBAPP_DB_NAME):
            logger.debug(u'tentamos atualizar modelo opac')
            if self.opac_model_instance is None:
                logger.debug(u'opac_model_instance is None. criamos nova instância')
                self.opac_model_instance = self.opac_model_class(**obj_dict)
                self.opac_model_instance.save()
                self.opac_model_instance.reload()
                logger.debug(u'novo modelo opac criado: _id = %s' % self.opac_model_instance._id)
            else:
                for k, v in obj_dict.iteritems():
                    self.opac_model_instance[k] = v
                self.opac_model_instance.save()

            logger.debug(u"modelo opac (_id: %s) encontrado. atualizando registro" % obj_dict['_id'])

        logger.debug(u"finalizando metodo prepare(uuid: %s)" % self.metadata['uuid'])
        logger.debug(u'opac_model_instance SALVO: %s' % self.opac_model_instance.to_json())
        return self.opac_model_instance

    def load(self):
        logger.debug(u"iniciando metodo load() (uuid: %s)" % self.metadata['uuid'])

        logger.debug(u"salvando modelo %s no opac (_id: %s)" % (
            self.opac_model_name, self.opac_model_instance._id))

        with switch_db(self.opac_model_class, OPAC_WEBAPP_DB_NAME):
            self.opac_model_instance.save()
            self.opac_model_instance.reload()
            logger.debug(u"modelo %s no opac (_id: %s) foi salvo" % (
                self.opac_model_name, self.opac_model_instance._id))

        logger.debug(u"salvando modelo %s no opac_proc (uuid: %s)" % (
            self.load_model_name, self.metadata['uuid']))

        with switch_db(self.load_model_class, OPAC_PROC_DB_NAME):
            self.metadata['process_finish_at'] = datetime.now()
            self.metadata['process_completed'] = True
            self.metadata['must_reprocess'] = False
            self.load_model_instance.update(**self.metadata)
            for field_to_load in self.fields_to_load:
                opac_field_value = self.opac_model_instance[field_to_load]
                self.load_model_instance[field_to_load] = opac_field_value
            self.load_model_instance.save()
            logger.debug(u"modelo %s no opac_proc (uuid: %s) foi atualizado" % (
                self.load_model_name, self.metadata['uuid']))

        logger.debug(u"finalizando metodo load() (uuid: %s)" % self.metadata['uuid'])
