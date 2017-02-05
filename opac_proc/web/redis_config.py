import os
# REDIS CONNECTION
REDIS_HOST = os.environ.get('OPAC_PROC_REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('OPAC_PROC_REDIS_PORT', 6379))
REDIS_PASSWORD = os.environ.get('OPAC_PROC_REDIS_PASSWORD', None)

REDIS_SETTINGS = {
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'password': REDIS_PASSWORD,
}

SENTRY_DSN = os.environ.get('OPAC_PROC_SENTRY_DSN', None)
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
