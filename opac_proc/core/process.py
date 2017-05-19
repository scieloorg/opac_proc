# coding: utf-8
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "extract")
else:
    logger = getMongoLogger(__name__, "INFO", "extract")


class Process(object):
    stage = 'default'
    collection_acronym = None
    r_queues = RQueues()
    db = get_db_connection()

    def create(self):
        self.r_queues.enqueue(
            self.stage,
            self.model_name,
            self.create_task)

    def update(self, ids=None):
        self.r_queues.enqueue(
            self.stage,
            self.model_name,
            self.update_task, ids)


class ProcessExtractBase(Process):
    stage = 'extract'


class ProcessTransformBase(Process):
    stage = 'transform'


class ProcessLoadBase(Process):
    stage = 'load'
