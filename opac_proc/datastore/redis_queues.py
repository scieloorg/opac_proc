# coding: utf-8
import os
import sys
from redis import Redis
from rq import Queue

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.web import config


class Singleton(object):
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instances[cls]


class RQueues(Singleton):
    redis_conn = None
    q_names = {
        'extract': {
            'collection': 'qex_collections',
            'journal': 'qex_journals',
            'issue': 'qex_issues',
            'article': 'qex_articles',
            'press_release': 'qex_press_releases',
        },
        'transform': {
            'collection': 'qtr_collections',
            'journal': 'qtr_journals',
            'issue': 'qtr_issues',
            'article': 'qtr_article',
            'press_release': 'qtr_press_releases',
        },
        'load': {
            'collection': 'qlo_collections',
            'journal': 'qlo_journals',
            'issue': 'qlo_issues',
            'article': 'qlo_articles',
            'press_release': 'qlo_press_releases',
        }
    }

    queues = {
        'extract': {
            'collection': None,
            'journal': None,
            'issue': None,
            'article': None,
            'press_release': None,
        },
        'transform': {
            'collection': None,
            'journal': None,
            'issue': None,
            'article': None,
            'press_release': None,
        },
        'load': {
            'collection': None,
            'journal': None,
            'issue': None,
            'article': None,
            'press_release': None,
        }
    }

    def __init__(self, redis_conn=None):
        if redis_conn:
            self.redis_conn = redis_conn
        else:
            self.redis_conn = Redis(**config.REDIS_SETTINGS)

    def create_queue(self, stage, model):
        queue = self.queues[stage][model]
        if queue is None:
            q_name = self.q_names[stage][model]
            queue = Queue(q_name, connection=self.redis_conn)
            self.queues[stage][model] = queue
        return queue

    def create_queues_for_stage(self, stage):
        for model in self.q_names[stage].keys():
            q = self.queues[stage][model]
            if q is None:
                self.queues[stage][model] = self.create_queue(stage, model)

    def get_queue(self, stage, model):
        queue = self.queues[stage][model]
        if queue is None:
            queue = self.create_queue(model, stage)
        return queue

    def enqueue(self, stage, model, task, *args, **kwargs):
        queue = self.get_queue(stage, model)
        return queue.enqueue(task, args=args, kwargs=kwargs, timeout=2000)
