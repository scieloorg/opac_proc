# coding: utf-8
import os
import sys
import logging
from mongoengine import connect, register_connection

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.web import config

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
        logger.info(msg)
        return db


def register_connections():
    # OPAC PROC
    opac_proc_db_name = get_opac_proc_db_name()
    logger.debug(u'Registrando conexão - {db}: mongo://{host}:{port}/{db}'.format(
        **config.MONGODB_SETTINGS))

    opac_proc_connection = {
        'name': opac_proc_db_name,
        'host': config.MONGODB_SETTINGS['host'],
        'port': config.MONGODB_SETTINGS['port'],
    }
    if 'username' in config.MONGODB_SETTINGS and 'password' in config.MONGODB_SETTINGS:
        opac_proc_connection['username'] = config.MONGODB_SETTINGS['username']
        opac_proc_connection['password'] = config.MONGODB_SETTINGS['password']

    register_connection(opac_proc_db_name, **opac_proc_connection)

    # OPAC WEBAPP
    opac_webapp_db_name = get_opac_webapp_db_name()
    logger.debug(u'Registrando conexão - {db}: mongo://{host}:{port}/{db}'.format(
        **config.OPAC_MONGODB_SETTINGS))

    opac_webapp_connection = {
        'name': opac_webapp_db_name,
        'host': config.OPAC_MONGODB_SETTINGS['host'],
        'port': config.OPAC_MONGODB_SETTINGS['port'],
    }

    if 'username' in config.OPAC_MONGODB_SETTINGS and 'password' in config.OPAC_MONGODB_SETTINGS:
        opac_webapp_connection['username'] = config.OPAC_MONGODB_SETTINGS['username']
        opac_webapp_connection['password'] = config.OPAC_MONGODB_SETTINGS['password']
    register_connection(opac_webapp_db_name, **opac_webapp_connection)

    # OPAC PROC LOGS
    opac_logs_db_name = get_opac_logs_db_name()
    logger.debug(u'Registrando conexão - {db}: mongo://{host}:{port}/{db}'.format(
        **config.OPAC_PROC_LOG_MONGODB_SETTINGS))

    opac_logs_connection = {
        'name': opac_logs_db_name,
        'host': config.OPAC_PROC_LOG_MONGODB_SETTINGS['host'],
        'port': config.OPAC_PROC_LOG_MONGODB_SETTINGS['port'],
    }

    if 'username' in config.OPAC_PROC_LOG_MONGODB_SETTINGS and 'password' in config.OPAC_PROC_LOG_MONGODB_SETTINGS:
        opac_logs_connection['username'] = config.OPAC_PROC_LOG_MONGODB_SETTINGS['username']
        opac_logs_connection['password'] = config.OPAC_PROC_LOG_MONGODB_SETTINGS['password']
    register_connection(opac_logs_db_name, **opac_logs_connection)
