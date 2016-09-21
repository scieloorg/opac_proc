# coding: utf-8
import os
import sys
import logging
from mongolog.handlers import MongoHandler

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(PROJECT_PATH)

from opac_proc.web import config


def getMongoLogger(name, level='INFO', process_stage='default'):
    """
    name = __name__
    level = 'DEBUG' ou 'INFO' ou 'WARNING' ou 'ERROR' ou 'CRITICAL'
    process_stage = 'extract' ou 'tranform' ou 'load' ou 'default'
    """

    logger = logging.getLogger(name)
    allowed_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    logging_level = allowed_levels.get(level, config.OPAC_PROC_LOG_LEVEL)
    logger.setLevel(logging_level)

    mongo_settings = {
        'collection': "%s_log" % process_stage,
        'db': config.OPAC_PROC_LOG_MONGODB_NAME,
        'host': config.MONGODB_SETTINGS['host'],
        'port': config.MONGODB_SETTINGS['port'],
    }
    if 'username' in config.MONGODB_SETTINGS.keys() and 'password' in config.MONGODB_SETTINGS.keys():
        mongo_settings['username'] = config.MONGODB_SETTINGS['username']
        mongo_settings['password'] = config.MONGODB_SETTINGS['password']

    mongo_handler = MongoHandler.to(**mongo_settings)
    logger.addHandler(mongo_handler)
    return logger
