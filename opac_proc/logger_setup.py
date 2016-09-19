# coding: utf-8
import sys
import os
import logging
from mongolog.handlers import MongoHandler

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(PROJECT_PATH)

from opac_proc.web import config


def getMongoLogger(name, level='INFO', process_stage='default'):

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

    collection_name = "%s_log" % process_stage
    mongo_handler = MongoHandler.to(db='mongolog', collection=collection_name)
    logger.addHandler(mongo_handler)
    return logger
