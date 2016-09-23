# coding: utf-8

from redis import Redis
from rq import Queue


class Singleton(object):
    _instances = {}

    def __new__(class_, *args, **kwargs):
        if class_ not in class_._instances:
            class_._instances[class_] = super(Singleton, class_).__new__(class_, *args, **kwargs)
        return class_._instances[class_]


class RQueues(Singleton):
    redis_conn = None
    q_names = {
        'extract': {
            'collection': 'qex_collections',
            'journal': 'qex_journals',
            'issue': 'qex_issues',
            'article': 'qex_articles',
        },
        'transform': {
            'collection': 'qtr_collections',
            'journal': 'qtr_journals',
            'issue': 'qtr_issues',
            'article': 'qtr_articles',
        },
        'load': {
            'collection': 'qlo_collections',
            'journal': 'qlo_journals',
            'issue': 'qlo_issues',
            'article': 'qlo_articles',
        }
    }

    queues = {
        'extract': {
            'collection': None,
            'journal': None,
            'issue': None,
            'article': None,
        },
        'transform': {
            'collection': None,
            'journal': None,
            'issue': None,
            'article': None,
        },
        'load': {
            'collection': None,
            'journal': None,
            'issue': None,
            'article': None,
        }
    }

    def __init__(self, redis_conn=None):
        if redis_conn:
            self.redis_conn = redis_conn
        else:
            self.redis_conn = Redis()  # usar configuarção

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
        return queue.enqueue(task, *args, **kwargs)
