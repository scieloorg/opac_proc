# coding: utf-8

import os
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))

# log level
OPAC_PROC_LOG_LEVEL = os.environ.get('OPAC_PROC_LOG_LEVEL', 'INFO')
# caminho absoluto (default) para o arquivo de log
OPAC_PROC_LOG_FILE_PATH_DEFAULT = '%s/logs/%s.log' % (
    HERE, datetime.datetime.now().strftime('%Y-%m-%d'))

# caminho absoluto para o arquivo de log
OPAC_PROC_LOG_FILE_PATH = os.environ.get(
    'OPAC_PROC_LOG_FILE_PATH',
    OPAC_PROC_LOG_FILE_PATH_DEFAULT)

# host e porta para conectar na API Thrift do Article meta ----------
ARTICLE_META_THRIFT_DOMAIN = os.environ.get(
    'OPAC_PROC_ARTICLE_META_THRIFT_DOMAIN',
    'articlemeta.scielo.org')
ARTICLE_META_THRIFT_PORT = int(os.environ.get(
    'OPAC_PROC_ARTICLE_META_THRIFT_PORT',
    11621))

# WEBAPP config: ----------------------------------------------------
DEBUG = bool(os.environ.get('OPAC_PROC_DEBUG', True))
TESTING = bool(os.environ.get('OPAC_PROC_TESTING', False))
SECRET_KEY = os.environ.get('OPAC_PROC_SECRET_KEY', "s3cr3t-k3y")
DEBUG_TB_INTERCEPT_REDIRECTS = False
OPAC_PROC_COLLECTION = os.environ.get('OPAC_PROC_COLLECTION', 'spa')

# CONEXÃO MONGO OPAC PROC --------------------------------------------
MONGODB_NAME = os.environ.get('OPAC_PROC_MONGODB_NAME', 'opac_proc')
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
OPAC_MONGODB_NAME = os.environ.get('OPAC_MONGODB_NAME', 'opac')
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
OPAC_PROC_LOG_MONGODB_NAME = os.environ.get('OPAC_PROC_LOG_MONGODB_NAME', 'opac_proc_logs')
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

# REDIS CONNECTION ---------------------------------------------
REDIS_HOST = os.environ.get('OPAC_PROC_REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('OPAC_PROC_REDIS_PORT', 6379))
REDIS_PASSWORD = os.environ.get('OPAC_PROC_REDIS_PASSWORD', None)

REDIS_SETTINGS = {
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'password': REDIS_PASSWORD,
}

QUEUES = [
    'qex_collections',
    'qex_journals',
    'qex_issues',
    'qex_articles',
    'qtr_collections',
    'qtr_journals',
    'qtr_issues',
    'qtr_articles',
    'qlo_collections',
    'qlo_journals',
    'qlo_issues',
    'qlo_article'
]

# Sentry -------------------------------------------------------
SENTRY_DSN = os.environ.get('OPAC_PROC_SENTRY_DSN', None)

# Metrics  -----------------------------------------------------
OPAC_METRICS_URL = os.environ.get('OPAC_METRICS_URL', 'http://analytics.scielo.org')

# Build Args ---------------------------------------------------
OPAC_PROC_BUILD_DATE = os.environ.get('OPAC_PROC_BUILD_DATE', None)
OPAC_PROC_VCS_REF = os.environ.get('OPAC_PROC_VCS_REF', None)
OPAC_PROC_WEBAPP_VERSION = os.environ.get('OPAC_PROC_WEBAPP_VERSION', None)


# Press Releases
RSS_PRESS_RELEASES_FEEDS_BY_CATEGORY = {
    'pt_BR': {
        'display_name': 'SciELO em Perspectiva Press Releases',
        'url': 'http://pressreleases.scielo.org/blog/category/{1}/feed/'
    },
    'es': {
        'display_name': 'SciELO en Perspectiva Press Releases',
        'url': 'http://pressreleases.scielo.org/{0}/category/press-releases/{1}/feed/',
    },
    'en': {
        'display_name': 'SciELO in Perspective Press Releases',
        'url': 'http://pressreleases.scielo.org/{0}/category/press-releases/{1}/feed/',
    },
}