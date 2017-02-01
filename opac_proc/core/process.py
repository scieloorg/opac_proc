# coding: utf-8


class Process(object):
    stage = 'default'
    collection_acronym = None

    def reprocess_collections(self, ids=None):
        raise NotImplementedError

    def reprocess_journals(self, ids=None):
        raise NotImplementedError

    def reprocess_issues(self, ids=None):
        raise NotImplementedError

    def reprocess_articles(self, ids=None):
        raise NotImplementedError

    def process_collection(self, collection_acronym=None, collection_uuid=None):
        raise NotImplementedError

    def process_journal(self, collection_acronym=None, issn=None, uuid=None):
        raise NotImplementedError

    def process_issue(self, collection_acronym=None, issue_pid=None, uuid=None):
        raise NotImplementedError

    def process_article(self, collection_acronym=None, article_pid=None, uuid=None):
        raise NotImplementedError

    def process_all_collections(self):
        raise NotImplementedError

    def process_all_journals(self):
        raise NotImplementedError

    def process_all_issues(self):
        raise NotImplementedError

    def process_all_articles(self):
        raise NotImplementedError
