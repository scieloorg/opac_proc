# coding: utf-8
from mongoengine.context_managers import switch_db
from bson.objectid import ObjectId

from opac_proc.datastore import models
from opac_proc.web.views.generics.list_views import ListView
from opac_proc.datastore.mongodb_connector import register_connections, get_opac_logs_db_name

from opac_proc.extractors.process import ExtractProcess

OPAC_PROC_LOGS_DB_NAME = get_opac_logs_db_name()


class ExtractCollectionListView(ListView):
    stage = 'extract'
    model_class = models.ExtractCollection
    model_name = 'collection'
    process_class = ExtractProcess

    can_create = True
    can_update = True
    can_delete = True
    page_title = "Extract: Collection"
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


class ExtractJournalListView(ListView):
    stage = 'extract'
    model_class = models.ExtractJournal
    model_name = 'journal'
    process_class = ExtractProcess

    can_create = True
    can_update = True
    can_delete = True
    page_title = "Extract: Journals"
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


class ExtractIssueListView(ListView):
    stage = 'extract'
    model_class = models.ExtractIssue
    model_name = 'issue'
    process_class = ExtractProcess

    can_create = True
    can_update = True
    can_delete = True
    page_title = "Extract: Issues"
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


class ExtractArticleListView(ListView):
    stage = 'extract'
    model_class = models.ExtractArticle
    model_name = 'article'
    process_class = ExtractProcess

    can_create = True
    can_update = True
    can_delete = True
    page_title = "Extract: Articles"
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

    list_filters = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'uuid'
        },
        {
            'field_label': u'PID',
            'field_name': 'pid',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update',
            'field_name': 'updated_at',
            'field_type': 'date_time'
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


class ExtractLogListView(ListView):
    stage = 'extract'
    model_class = models.ExtractLog
    model_name = 'loadlog'
    process_class = None  # logs somente tem o Delete

    can_create = False
    can_update = False
    can_delete = True
    page_title = "Extract: Logs"
    page_subtitle = "most recent first"
    per_page = 50
    list_colums = [
        {
            'field_label': u'Timestamp',
            'field_name': 'time',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Name',
            'field_name': 'name',
            'field_type': 'string'
        },
        {
            'field_label': u'Function',
            'field_name': 'funcName',
            'field_type': 'string'
        },
        {
            'field_label': u'Message',
            'field_name': 'message',
            'field_type': 'string'
        },
        {
            'field_label': u'Line',
            'field_name': 'lineno',
            'field_type': 'string'
        },
        {
            'field_label': u'Level',
            'field_name': 'levelname',
            'field_type': 'string'
        },
    ]

    def get_objects(self):
        register_connections()
        with switch_db(self.model_class, OPAC_PROC_LOGS_DB_NAME):
            return self.model_class.objects.order_by('-time')

    def do_delete_all(self):
        register_connections()
        with switch_db(self.model_class, OPAC_PROC_LOGS_DB_NAME):
            super(ExtractLogListView, self).do_delete_all()

    def do_delete_selected(self, ids):
        register_connections()
        with switch_db(self.model_class, OPAC_PROC_LOGS_DB_NAME):
            super(ExtractLogListView, self).do_delete_selected(ids)

    def get_selected_ids(self):
        ids = super(ExtractLogListView, self).get_selected_ids()
        return [ObjectId(id.strip()) for id in ids]
