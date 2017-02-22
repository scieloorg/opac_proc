# coding: utf-8
from mongoengine.context_managers import switch_db
from bson.objectid import ObjectId

from opac_proc.datastore import models
from opac_proc.web.views.generics.list_views import ListView
from opac_proc.datastore.mongodb_connector import register_connections, get_opac_logs_db_name
from opac_proc.transformers.process import TransformProcess

OPAC_PROC_LOGS_DB_NAME = get_opac_logs_db_name()


class TransformBaseListView(ListView):
    stage = 'transform'
    process_class = TransformProcess
    can_create = True
    can_update = True
    can_delete = True


class TransformCollectionListView(TransformBaseListView):
    model_class = models.TransformCollection
    model_name = 'collection'
    page_title = "Transform: Collection"
    list_columns = [
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

    list_filters = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'uuid'
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
            'field_label': u'Last update',
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


class TransformJournalListView(TransformBaseListView):
    model_class = models.TransformJournal
    model_name = 'journal'
    page_title = "Transform: Journals"
    list_columns = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'ISSN',
            'field_name': 'acronym',
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

    list_filters = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'uuid'
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


class TransformIssueListView(TransformBaseListView):
    model_class = models.TransformIssue
    model_name = 'issue'
    page_title = "Transform: Issues"
    list_columns = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'Label',
            'field_name': 'label',
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


class TransformArticleListView(TransformBaseListView):
    model_class = models.TransformArticle
    model_name = 'article'
    page_title = "Transform: Articles"
    list_columns = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'PID',
            'field_name': 'pid',
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


class TransformLogListView(TransformBaseListView):
    model_class = models.TransformLog
    model_name = 'transformlog'
    process_class = None  # logs somente tem o Delete

    can_create = False
    can_update = False
    can_delete = True
    page_title = "Transform: Logs"
    page_subtitle = "most recent first"
    per_page = 50
    list_columns = [
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

    list_filters = [
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
            'field_label': u'Level',
            'field_name': 'levelname',
            'field_type': 'choices',
            'field_options': (
                ('DEBUG', 'DEBUG'),
                ('INFO', 'INFO'),
                ('WARNING', 'WARNING'),
                ('ERROR', 'ERROR'),
                ('CRITICAL', 'CRITICAL'),
            )
        },
    ]

    def get_objects(self):
        register_connections()
        with switch_db(self.model_class, OPAC_PROC_LOGS_DB_NAME):
            objects = super(TransformLogListView, self).get_objects()
            return objects.order_by('-time')

    def do_delete_all(self):
        register_connections()
        with switch_db(self.model_class, OPAC_PROC_LOGS_DB_NAME):
            super(TransformLogListView, self).do_delete_all()

    def do_delete_selected(self, ids):
        register_connections()
        with switch_db(self.model_class, OPAC_PROC_LOGS_DB_NAME):
            super(TransformLogListView, self).do_delete_selected(ids)

    def get_selected_ids(self):
        ids = super(TransformLogListView, self).get_selected_ids()
        return [ObjectId(id.strip()) for id in ids]
