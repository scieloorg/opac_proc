# coding: utf-8
import os
import sys
import logging
from mongoengine import connect, register_connection

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.web import config  # noqa

logger = logging.getLogger(__name__)


def get_opac_proc_db_name():
    return config.MONGODB_NAME


def get_opac_webapp_db_name():
    return config.OPAC_MONGODB_NAME


def get_opac_logs_db_name():
    return config.OPAC_PROC_LOG_MONGODB_NAME


def get_db_connection():
    if config.MONGODB_USER and config.MONGODB_PASS:
        msg = u'Iniciando conexão - com credenciais do banco: mongo://{username}:{password}@{host}:{port}/{db}'.format(
            **config.MONGODB_SETTINGS)
        logger.debug(msg)
    else:
        msg = u'Iniciando conexão - sem credenciais do banco: mongo://{host}:{port}/{db}'.format(
            **config.MONGODB_SETTINGS)
        logger.debug(msg)
    try:
        db = connect(**config.MONGODB_SETTINGS)
    except Exception, e:   # melhorar captura da Exceção
        msg = u"Não é possível conectar com banco de dados mongo. %s", str(e)
        logger.error(msg)
    else:
        db_name = get_opac_proc_db_name()
        msg = u"Conexão establecida com banco: %s!" % db_name
        logger.debug(msg)
        return db


def get_connection_credentials(mongo_settings_dict):
    credentials = {
        'name': mongo_settings_dict['db'],
        'host': mongo_settings_dict['host'],
        'port': mongo_settings_dict['port']
    }
    if 'username' in mongo_settings_dict and 'password' in mongo_settings_dict:
        credentials['username'] = mongo_settings_dict['username']
        credentials['password'] = mongo_settings_dict['password']
    return credentials


def register_connections():
    # OPAC PROC
    logger.debug(u'Registrando conexão - {db}: mongo://{host}:{port}/{db}'.format(
        **config.MONGODB_SETTINGS))
    opac_proc_db_credentials = get_connection_credentials(config.MONGODB_SETTINGS)
    opac_proc_db_name = get_opac_proc_db_name()
    register_connection(opac_proc_db_name, **opac_proc_db_credentials)

    # OPAC WEBAPP
    logger.debug(u'Registrando conexão - {db}: mongo://{host}:{port}/{db}'.format(
        **config.OPAC_MONGODB_SETTINGS))
    opac_webapp_db_credentials = get_connection_credentials(config.OPAC_MONGODB_SETTINGS)
    opac_webapp_db_name = get_opac_webapp_db_name()
    register_connection(opac_webapp_db_name, **opac_webapp_db_credentials)

    # OPAC PROC LOGS
    logger.debug(u'Registrando conexão - {db}: mongo://{host}:{port}/{db}'.format(
        **config.OPAC_PROC_LOG_MONGODB_SETTINGS))
    opac_logs_db_credentials = get_connection_credentials(config.OPAC_PROC_LOG_MONGODB_SETTINGS)
    opac_logs_db_name = get_opac_logs_db_name()
    register_connection(opac_logs_db_name, **opac_logs_db_credentials)
