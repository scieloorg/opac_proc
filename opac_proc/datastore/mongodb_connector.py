# coding: utf-8
from __future__ import unicode_literals
import logging
from mongoengine import connect

import config

logger = logging.getLogger(__name__)


def get_db_connection():
    if config.MONGODB_USER and config.MONGODB_PASS:
        logger.debug('Iniciando conexão - com credenciais do banco: mongo://{username}:{password}@{host}:{port}/{db}'.format(**config.MONGODB_SETTINGS))
    else:
        logger.debug('Iniciando conexão - sem credenciais do banco: mongo://{host}:{port}/{db}'.format(**config.MONGODB_SETTINGS))
    try:
        db = connect(**config.MONGODB_SETTINGS)
    except Exception, e:   # melhorar captura da Exceção
        logger.error("Não é possível conectar com banco de dados mongo", str(e))
    else:
        db_name = config.MONGODB_SETTINGS['db']
        logger.info("Conexão establecida com banco: %s!" % db_name)
        return db
