# coding: utf-8

"""
    Copia do `config.py` com as settings para usar no testing`
"""

import os
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))

# log level
OPAC_PROC_LOG_LEVEL = 'INFO'
# caminho absoluto (default) para o arquivo de log
OPAC_PROC_LOG_FILE_PATH_DEFAULT = '%s/logs/testing_%s.log' % (
    HERE, datetime.datetime.now().strftime('%Y-%m-%d'))

# caminho absoluto para o arquivo de log
OPAC_PROC_LOG_FILE_PATH = OPAC_PROC_LOG_FILE_PATH_DEFAULT

# WEBAPP config: ----------------------------------------------------
DEBUG = False
TESTING = True
SECRET_KEY = 'testing-s3cr3t-k3y'
DEBUG_TB_INTERCEPT_REDIRECTS = False

# CONEXÃO MONGO OPAC PROC --------------------------------------------
MONGODB_NAME = 'opac_proc_testing'
MONGODB_HOST = os.environ.get('OPAC_PROC_MONGODB_HOST', 'localhost')
MONGODB_PORT = os.environ.get('OPAC_PROC_MONGODB_PORT', 27017)
MONGODB_USER = os.environ.get('OPAC_PROC_MONGODB_USER', None)
MONGODB_PASS = os.environ.get('OPAC_PROC_MONGODB_PASS', None)

MONGODB_SETTINGS = {
    'db': MONGODB_NAME,
    'host': MONGODB_HOST,
    'port': int(MONGODB_PORT),
}

if MONGODB_USER and MONGODB_PASS:
    MONGODB_SETTINGS['username'] = MONGODB_USER
    MONGODB_SETTINGS['password'] = MONGODB_PASS

# CONEXÃO MONGO OPAC WEB APP -----------------------------------------
OPAC_MONGODB_NAME = 'opac_testing'
OPAC_MONGODB_HOST = os.environ.get('OPAC_MONGODB_HOST', 'localhost')
OPAC_MONGODB_PORT = os.environ.get('OPAC_MONGODB_PORT', 27017)
OPAC_MONGODB_USER = os.environ.get('OPAC_MONGODB_USER', None)
OPAC_MONGODB_PASS = os.environ.get('OPAC_MONGODB_PASS', None)

OPAC_MONGODB_SETTINGS = {
    'db': OPAC_MONGODB_NAME,
    'host': OPAC_MONGODB_HOST,
    'port': int(OPAC_MONGODB_PORT),
}

if OPAC_MONGODB_USER and OPAC_MONGODB_PASS:
    OPAC_MONGODB_SETTINGS['username'] = OPAC_MONGODB_USER
    OPAC_MONGODB_SETTINGS['password'] = OPAC_MONGODB_PASS


# CONEXÃO MONGO OPAC PROC LOGS ---------------------------------------
OPAC_PROC_LOG_MONGODB_NAME = 'opac_proc_logs_testing'
OPAC_PROC_LOG_MONGODB_HOST = os.environ.get('OPAC_PROC_LOG_MONGODB_HOST', 'localhost')
OPAC_PROC_LOG_MONGODB_PORT = os.environ.get('OPAC_PROC_LOG_MONGODB_PORT', 27017)
OPAC_PROC_LOG_MONGODB_USER = os.environ.get('OPAC_PROC_LOG_MONGODB_USER', None)
OPAC_PROC_LOG_MONGODB_PASS = os.environ.get('OPAC_PROC_LOG_MONGODB_PASS', None)

OPAC_PROC_LOG_MONGODB_SETTINGS = {
    'db': OPAC_PROC_LOG_MONGODB_NAME,
    'host': OPAC_PROC_LOG_MONGODB_HOST,
    'port': int(OPAC_PROC_LOG_MONGODB_PORT),
}

if OPAC_PROC_LOG_MONGODB_USER and OPAC_PROC_LOG_MONGODB_PASS:
    OPAC_PROC_LOG_MONGODB_SETTINGS['username'] = OPAC_PROC_LOG_MONGODB_USER
    OPAC_PROC_LOG_MONGODB_SETTINGS['password'] = OPAC_PROC_LOG_MONGODB_PASS
