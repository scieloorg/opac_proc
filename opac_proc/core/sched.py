# coding: utf-8
import os
import sys
import logging
import logging.config

from flask import current_app
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler


PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)


logger = logging.getLogger(__name__)
logger_ini = os.path.join(os.path.dirname(__file__), 'logging.ini')
logging.config.fileConfig(logger_ini, disable_existing_loggers=False)


class SyncScheduler:

    q_names = {
        'extract': {
            'collection': 'qex_collections',
            'journal': 'qex_journals',
            'issue': 'qex_issues',
            'article': 'qex_articles',
            'press_release': 'qex_press_releases',
            'news': 'qex_news',
        },
        'transform': {
            'collection': 'qtr_collections',
            'journal': 'qtr_journals',
            'issue': 'qtr_issues',
            'article': 'qtr_articles',
            'press_release': 'qtr_press_releases',
            'news': 'qtr_news',
        },
        'load': {
            'collection': 'qlo_collections',
            'journal': 'qlo_journals',
            'issue': 'qlo_issues',
            'article': 'qlo_articles',
            'press_release': 'qlo_press_releases',
            'news': 'qlo_news',
        },
        'sync_ids': {
            'collection': 'qss_collections',
            'journal': 'qss_journals',
            'issue': 'qss_issues',
            'article': 'qss_articles',
            'press_release': 'qss_press_releases',
            'news': 'qss_news',
        }
    }

    model_name = ''  # definir na subclasse
    stage = ''  # definir na subclasse
    cron_string = None  # definir na subclasse
    task_func = None  # definir na subclasse
    task_args = None  # definir na subclasse

    queue_name = None
    _queue = None
    _redis_conn = None
    _rq_scheduler_instance = None

    def __init__(self):
        self._redis_conn = Redis(**current_app.config['REDIS_SETTINGS'])
        self.queue_name = self.q_names[self.stage][self.model_name]

        self.queue = Queue(self.queue_name, connection=self._redis_conn)
        self._rq_scheduler_instance = Scheduler(
            queue=self._queue,
            connection=self._redis_conn)

    def setup(self):
        rq_sched = self._rq_scheduler_instance

        if self.task_func:
            rq_sched.cron(
                self.cron_string,
                func=self.task_func,
                args=self.task_args,
                queue_name=self.queue_name)
        else:
            raise AttributeError(u'Falta definir a função da task e/ou args')

    def get_scheduler_instance(self):
        return self._rq_scheduler_instance

    def clear_jobs(self):
        rq_sched = self._rq_scheduler_instance

        for job in rq_sched.get_jobs():
            if job.origin == self.queue_name:
                logger.info('[scheduler: %s]removendo job %s do scheduler' % (
                    self.model_name, job.id))
                rq_sched.cancel(job)
