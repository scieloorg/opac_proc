# coding: utf-8
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import get_db_connection


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

    def delete_selected(self, selected_uuids):
        self.r_queues.enqueue(
            self.stage,
            self.model_name,
            self.task_delete_selected, selected_uuids)

    def delete_all(self):
        self.r_queues.enqueue(
            self.stage,
            self.model_name,
            self.task_delete_all)


class ProcessIdentifiersBase(Process):
    stage = 'sync_ids'


class ProcessExtractBase(Process):
    stage = 'extract'


class ProcessTransformBase(Process):
    stage = 'transform'


class ProcessLoadBase(Process):
    stage = 'load'
