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

    def selected(self, selected_uuids):
        self.r_queues.enqueue(
            self.stage,
            self.model_name,
            self.task_for_selected, selected_uuids)

    def all(self):
        self.r_queues.enqueue(
            self.stage,
            self.model_name,
            self.task_for_all)


class ProcessExtractBase(Process):
    stage = 'extract'


class ProcessTransformBase(Process):
    stage = 'transform'


class ProcessLoadBase(Process):
    stage = 'load'
