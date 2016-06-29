# coding: utf-8

import os
import datetime
from datetime import timedelta

FROM_DATE = (datetime.datetime.now()-timedelta(60)).isoformat()[:10]

ARTICLE_META_URL = 'http://articlemeta.scielo.org/'

ARTICLE_META_THRIFT_URL = 'articlemeta.scielo.org'
ARTICLE_META_THRIFT_PORT = 11720

APP_URL = 'http://homolog.opac.scielo.org'

MONGODB_DBNAME = os.environ.get('OPAC_MONGO_DB_DBNAME', 'opac')
MONGODB_HOST = os.environ.get('OPAC_MONGO_PORT_27017_TCP_ADDR', 'localhost')
MONGODB_PORT = os.environ.get('OPAC_MONGO_PORT_27017_TCP_PORT', 27017)

MONGODB_SETTINGS = {
    'db': MONGODB_DBNAME,
    'host': MONGODB_HOST,
    'port': int(MONGODB_PORT),
}
