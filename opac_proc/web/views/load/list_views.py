# coding: utf-8
from opac_proc.datastore import models
from opac_proc.web.views.generics.list_views import ListView


class LoadCollectionListView(ListView):
    # panel_title = u"Lista de todas as coleções coletadas na operação: extração"
    page_title = "Load: Collection"
    list_colums = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'Acrônimo',
            'field_name': 'acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'Nome',
            'field_name': 'name',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update:',
            'field_name': 'updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Deleted?',
            'field_name': 'is_deleted',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Process completed?',
            'field_name': 'process_completed',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Must reprocess?',
            'field_name': 'must_reprocess',
            'field_type': 'boolean'
        },
    ]

    def get_objects(self):
        return models.LoadCollection.objects()


class LoadJournalListView(ListView):
    page_title = "Load: Journals"
    list_colums = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'ISSN',
            'field_name': 'code',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update:',
            'field_name': 'updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Deleted?',
            'field_name': 'is_deleted',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Process completed?',
            'field_name': 'process_completed',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Must reprocess?',
            'field_name': 'must_reprocess',
            'field_type': 'boolean'
        },
    ]

    def get_objects(self):
        return models.LoadJournal.objects()


class LoadIssueListView(ListView):
    page_title = "Load: Issues"
    list_colums = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'PID',
            'field_name': 'code',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update:',
            'field_name': 'updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Deleted?',
            'field_name': 'is_deleted',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Process completed?',
            'field_name': 'process_completed',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Reprocess?',
            'field_name': 'must_reprocess',
            'field_type': 'boolean'
        },
    ]

    def get_objects(self):
        return models.LoadIssue.objects()


class LoadArticleListView(ListView):
    page_title = "Load: Articles"
    list_colums = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'PID',
            'field_name': 'code',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update:',
            'field_name': 'updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Deleted?',
            'field_name': 'is_deleted',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Process completed?',
            'field_name': 'process_completed',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Reprocess?',
            'field_name': 'must_reprocess',
            'field_type': 'boolean'
        },
    ]

    def get_objects(self):
        return models.LoadArticle.objects()
