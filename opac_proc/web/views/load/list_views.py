# coding: utf-8
from mongoengine.context_managers import switch_db
from bson.objectid import ObjectId
from flask import request, flash
from opac_proc.datastore import models
from opac_proc.web.views.generics.list_views import ListView
from opac_proc.datastore.mongodb_connector import register_connections, get_opac_logs_db_name

OPAC_PROC_LOGS_DB_NAME = get_opac_logs_db_name()


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


class LoadLogListView(ListView):
    page_title = "Load: Logs"
    page_subtitle = "most recent first"
    per_page = 50
    can_create = False
    can_update = False
    can_delete = True
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
        with switch_db(models.LoadLog, OPAC_PROC_LOGS_DB_NAME):
            return models.LoadLog.objects.order_by('-time')

    def do_delete_all(self):
        register_connections()
        with switch_db(models.LoadLog, OPAC_PROC_LOGS_DB_NAME):
            models.LoadLog.objects.all().delete()
        flash('All records deleted successfully!', 'success')

    def do_delete_selected(self, ids):
        register_connections()
        delete_errors_count = 0
        with switch_db(models.LoadLog, OPAC_PROC_LOGS_DB_NAME):
            for oid in ids:
                try:
                    model = models.LoadLog.objects(pk=oid).first()
                    model.delete()
                except Exception as e:
                    delete_errors_count += 1
        if delete_errors_count:
            flash('%s records cannot be deleted' % delete_errors_count, 'error')
        successfully_deleted = len(ids) - delete_errors_count
        if successfully_deleted > 0:
            flash('%s records deleted successfully!' % successfully_deleted, 'success')
        else:
            flash('%s records deleted successfully!' % successfully_deleted, 'warning')

    def get_selected_ids(self):
        ids = request.form.getlist('rowid')
        if not ids:
            raise ValueError("No records selected")
        elif isinstance(ids, list):
            ids = [ObjectId(id.strip()) for id in ids]
        else:
            raise ValueError("Invalid selection %s" % ids)
        return ids
