# coding: utf-8
from opac_proc.core.process import Process


class ExtractProcess(Process):
    stage = 'extract'
    collection_acronym = None
    async = True

    def __init__(self, collection_acronym, async=True):
        self.collection_acronym = collection_acronym
        self.async = async

    def reprocess_collection():
        pass

    def reprocess_journal():
        pass

    def reprocess_issue():
        pass

    def reprocess_article():
        pass

    def reprocess_all():
        pass

    def process_collection():
        pass

    def process_journal():
        pass

    def process_issue():
        pass

    def process_article():
        pass

    def process_all():
        pass
