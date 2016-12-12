# coding: utf-8

from opac_proc.datastore.redis_queues import RQueues
from opac_proc.datastore.mongodb_connector import get_db_connection


class Process(object):
    stage = 'default'
    collection_acronym = None
    async = True

    def reprocess_collection():
        raise NotImplemented

    def reprocess_journal():
        raise NotImplemented

    def reprocess_issue():
        raise NotImplemented

    def reprocess_article():
        raise NotImplemented

    def reprocess_all():
        raise NotImplemented

    def process_collection():
        raise NotImplemented

    def process_journal():
        raise NotImplemented

    def process_issue():
        raise NotImplemented

    def process_article():
        raise NotImplemented

    def process_all():
        raise NotImplemented
