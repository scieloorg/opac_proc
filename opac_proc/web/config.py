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
DEBUG = os.environ.get('OPAC_PROC_DEBUG', 'False') == 'True'
TESTING = os.environ.get('OPAC_PROC_TESTING', 'False') == 'True'
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

# News
RSS_NEWS_FEEDS = {
    'pt_BR': {
        'display_name': 'SciELO em Perspectiva',
        'url': 'http://blog.scielo.org/feed/'
    },
    'es': {
        'display_name': 'SciELO en Perspectiva',
        'url': 'http://blog.scielo.org/es/feed/',
    },
    'en': {
        'display_name': 'SciELO in Perspective',
        'url': 'http://blog.scielo.org/en/feed/',
    },
}

OPAC_PROC_ARTICLE_EXTRACTION_WITH_BODY = os.environ.get('OPAC_PROC_ARTICLE_EXTRACTION_WITH_BODY', 'True') == 'True'

OPAC_SSM_GRPC_SERVER_HOST = os.environ.get('OPAC_SSM_GRPC_SERVER_HOST', 'homolog.grpc.ssm.scielo.org')
OPAC_SSM_GRPC_SERVER_PORT = os.environ.get('OPAC_SSM_GRPC_SERVER_PORT', '8005')

# Raise erro if it is 'True' or log erro if 'False'
OPAC_PROC_RAISE_ERROR = os.environ.get('OPAC_PROC_RAISE_ERROR', 'False') == 'True'

OPAC_PROC_ASSETS_SOURCE_PDF_PATH = os.environ.get('OPAC_PROC_ASSETS_SOURCE_PDF_PATH', '/app/data/pdf')
OPAC_PROC_ASSETS_SOURCE_XML_PATH = os.environ.get('OPAC_PROC_ASSETS_SOURCE_XML_PATH', '/app/data/xml')
OPAC_PROC_ASSETS_SOURCE_MEDIA_PATH = os.environ.get('OPAC_PROC_ASSETS_SOURCE_MEDIA_PATH', '/app/data/img')

OPAC_PROC_ARTICLE_CSS_URL = os.environ.get('OPAC_PROC_ARTICLE_CSS_URL', 'https://ssm.scielo.org/media/assets/css/scielo-article.css')
OPAC_PROC_ARTICLE_PRINT_CSS_URL = os.environ.get('OPAC_PROC_ARTICLE_PRINT_CSS_URL', 'https://ssm.scielo.org/media/assets/css/scielo-print.css')
OPAC_PROC_ARTICLE_JS_URL = os.environ.get('OPAC_PROC_ARTICLE_JS_URL', 'https://ssm.scielo.org/media/assets/js/scielo-article.js')

OPAC_PROC_MEDIA_XML_MATCH_REGEX = os.environ.get('OPAC_PROC_IMG_XML_MATCH_REGEX', 'href="([^/\s]+\.(?:tiff|tif|jpg|jpeg|gif|png|svg))"')
OPAC_PROC_MEDIA_HTML_MATCH_REGEX = os.environ.get('OPAC_PROC_IMG_HTML_MATCH_REGEX', 'src="([^"]+)"')
OPAC_PROC_MEDIA_ARROW_MATCH_REGEXS = os.environ.get('OPAC_PROC_MEDIA_ARROW_MATCH_REGEXS', '<a href="#top">(.*?)</a>,<a href="#enda">(.*?)</a>,<a href="#up">(.*?)</a>')
OPAC_PROC_MEDIA_ARROW_REPLACE = os.environ.get('OPAC_PROC_MEDIA_ARROW_REPLACE', '<a href="#top">&#9650;</a>')

# Habilitar/Desabilitar o form de registro
WEB_REGISTRATION_ENABLED = os.environ.get('OPAC_PROC_WEB_REGISTRATION_ENABLED', 'False') == 'True'
# True/False para requerir ou não confirmação de email no processo de registro/login
ACCOUNTS_REQUIRES_EMAIL_CONFIRMATION = os.environ.get('OPAC_PROC_ACCOUNTS_REQUIRES_EMAIL_CONFIRMATION', 'True') == 'True'

# Tempo de expiração para os tokens. Valor en segundos: 86400 = 60*60*24 = 1 dia
TOKEN_MAX_AGE = 86400

# Credenciais para envio de emails:
DEFAULT_EMAIL = os.environ.get('OPAC_PROC_DEFAULT_EMAIL', 'scielo@scielo.org')
MAIL_SERVER = os.environ.get('OPAC_PROC_MAIL_SERVER', 'localhost')
MAIL_PORT = int(os.environ.get('OPAC_PROC_MAIL_PORT', 1025))
MAIL_USE_TLS = os.environ.get('OPAC_PROC_MAIL_USE_TLS', 'False') == 'True'
MAIL_USE_SSL = os.environ.get('OPAC_PROC_MAIL_USE_SSL', 'False') == 'True'
MAIL_DEBUG = DEBUG
MAIL_USERNAME = os.environ.get('OPAC_PROC_MAIL_USERNAME', None)
MAIL_PASSWORD = os.environ.get('OPAC_PROC_MAIL_PASSWORD', None)
MAIL_DEFAULT_SENDER = DEFAULT_EMAIL
MAIL_MAX_EMAILS = None
MAIL_ASCII_ATTACHMENTS = False

# Processamento parcial:
DEFAULT_DIFF_SPAN = int(os.environ.get('OPAC_PROC_DEFAULT_DIFF_SPAN_DAYS', 7))
