# coding: utf-8
import os
import sys
from mongoengine import connect, register_connection

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "load")
else:
    logger = getMongoLogger(__name__, "INFO", "load")


def get_opac_proc_db_name():
    return config.MONGODB_NAME


def get_opac_webapp_db_name():
    return config.OPAC_MONGODB_NAME


def get_opac_logs_db_name():
    return config.OPAC_PROC_LOG_MONGODB_NAME


def get_db_connection():
    if config.MONGODB_USER and config.MONGODB_PASS:
        logger.debug(u'Iniciando conexão - com credenciais do banco: mongo://{username}:{password}@{host}:{port}/{db}'.format(**config.MONGODB_SETTINGS))
    else:
        logger.debug(u'Iniciando conexão - sem credenciais do banco: mongo://{host}:{port}/{db}'.format(**config.MONGODB_SETTINGS))
    try:
        db = connect(**config.MONGODB_SETTINGS)
    except Exception, e:   # melhorar captura da Exceção
        logger.error(u"Não é possível conectar com banco de dados mongo", str(e))
    else:
        db_name = get_opac_proc_db_name()
        logger.info(u"Conexão establecida com banco: %s!" % db_name)
        return db


def register_connections():
    # OPAC PROC
    opac_proc_db_name = get_opac_proc_db_name()
    logger.debug(u'Registrando conexão - {db}: mongo://{host}:{port}/{db}'.format(
        **config.MONGODB_SETTINGS))
    register_connection(opac_proc_db_name, opac_proc_db_name)

    # OPAC WEBAPP
    opac_db_name = get_opac_webapp_db_name()
    logger.debug(u'Registrando conexão - {db}: mongo://{host}:{port}/{db}'.format(
        **config.OPAC_MONGODB_SETTINGS))
    register_connection(opac_db_name, opac_db_name)

    # OPAC PROC LOGS
    opac_logs_db_name = get_opac_logs_db_name()
    logger.debug(u'Registrando conexão de logs - {db}'.format(db=opac_logs_db_name))
    register_connection(opac_logs_db_name, opac_logs_db_name)
