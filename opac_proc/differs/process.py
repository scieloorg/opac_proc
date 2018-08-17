# coding: utf-8
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import get_db_connection


class ProcessDiffersBase:
    model_name = ''
    collection_acronym = None
    r_queues = RQueues()
    db = get_db_connection()

    task_produce_add = 'opac_proc.differs.produce_jobs.task_produce_diff_add'
    task_produce_update = 'opac_proc.differs.produce_jobs.task_produce_diff_update'
    task_produce_delete = 'opac_proc.differs.produce_jobs.task_produce_diff_delete'
    task_delete_selected = 'opac_proc.differs.produce_jobs.task_delete_selected_diff_etl_model'
    task_delete_all = 'opac_proc.differs.produce_jobs.task_delete_all_diff_etl_model'
    task_consume_add = 'opac_proc.differs.consumer_jobs.task_consume_diff_add'
    task_consume_update = 'opac_proc.differs.consumer_jobs.task_consume_diff_update'
    task_consume_delete = 'opac_proc.differs.consumer_jobs.task_consume_diff_delete'

    def produce(self, stage, action):
        task_fn = None
        if action == 'add':
            task_fn = self.task_produce_add
        elif action == 'update':
            task_fn = self.task_produce_update
        elif action == 'delete':
            task_fn = self.task_produce_delete
        else:
            raise ValueError(u'Param: action %s é inválido' % action)

        self.r_queues.enqueue(
            'sync_ids',
            self.model_name,
            task_fn,
            stage, self.model_name)  # task args

    def consume(self, stage, action):
        task_fn = None
        if action == 'add':
            task_fn = self.task_consume_add
        elif action == 'update':
            task_fn = self.task_consume_update
        elif action == 'delete':
            task_fn = self.task_consume_delete
        else:
            raise ValueError(u'Param: action %s é inválido' % action)

        self.r_queues.enqueue(
            'sync_ids',
            self.model_name,
            task_fn,
            stage, self.model_name)  # task args

    def delete_selected(self, stage, action, selected_uuids):
        self.r_queues.enqueue(
            'sync_ids',
            self.model_name,
            self.task_delete_selected,
            stage, self.model_name, action, selected_uuids)  # task args

    def delete_all(self, stage, action):
        self.r_queues.enqueue(
            'sync_ids',
            self.model_name,
            self.task_delete_all,
            stage, self.model_name, action)  # task args


class ProcessDiffCollection(ProcessDiffersBase):
    model_name = 'collection'


class ProcessDiffJournal(ProcessDiffersBase):
    model_name = 'journal'


class ProcessDiffIssue(ProcessDiffersBase):
    model_name = 'issue'


class ProcessDiffArticle(ProcessDiffersBase):
    model_name = 'article'


class ProcessDiffPressRelease(ProcessDiffersBase):
    model_name = 'press_release'


class ProcessDiffNews(ProcessDiffersBase):
    model_name = 'news'
