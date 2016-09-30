# coding: utf-8
from mongoengine.context_managers import switch_db
from opac_proc.datastore import models
from opac_proc.web.views.generics.list_views import ListView
from opac_proc.datastore.mongodb_connector import register_connections, get_opac_logs_db_name

from opac_proc.extractors.process import ExtractProcess

OPAC_PROC_LOGS_DB_NAME = get_opac_logs_db_name()


class ExtractCollectionListView(ListView):
    # panel_title = u"Lista de todas as coleções coletadas na operação: extração"
    page_title = "Extract: Collection"
    can_create = True
    can_update = True
    can_delete = True
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
        return models.ExtractCollection.objects()

    def do_create(self):
        ex_processor = ExtractProcess()
        raise NotImplemented

    def do_update_all(self):
        raise NotImplemented

    def do_update_selected(self, ids):
        raise NotImplemented

    def do_delete_all(self):
        raise NotImplemented

    def do_delete_selected(self, ids):
        raise NotImplemented


class ExtractJournalListView(ListView):
    page_title = "Extract: Journals"
    can_create = True
    can_update = True
    can_delete = True
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
        return models.ExtractJournal.objects()

    def do_create(self):
        ex_processor = ExtractProcess()
        raise NotImplemented

    def do_update_all(self):
        raise NotImplemented

    def do_update_selected(self, ids):
        raise NotImplemented

    def do_delete_all(self):
        raise NotImplemented

    def do_delete_selected(self, ids):
        raise NotImplemented


class ExtractIssueListView(ListView):
    page_title = "Extract: Issues"
    can_create = True
    can_update = True
    can_delete = True
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
        return models.ExtractIssue.objects()

    def do_create(self):
        ex_processor = ExtractProcess()
        raise NotImplemented

    def do_update_all(self):
        raise NotImplemented

    def do_update_selected(self, ids):
        raise NotImplemented

    def do_delete_all(self):
        raise NotImplemented

    def do_delete_selected(self, ids):
        raise NotImplemented


class ExtractArticleListView(ListView):
    page_title = "Extract: Articles"
    can_create = True
    can_update = True
    can_delete = True
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
        return models.ExtractArticle.objects()

    def do_create(self):
        ex_processor = ExtractProcess()
        raise NotImplemented

    def do_update_all(self):
        raise NotImplemented

    def do_update_selected(self, ids):
        raise NotImplemented

    def do_delete_all(self):
        raise NotImplemented

    def do_delete_selected(self, ids):
        raise NotImplemented


class ExtractLogListView(ListView):
    page_title = "Extract: Logs"
    page_subtitle = "most recent first"
    per_page = 50
    can_create = True
    can_update = True
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
        with switch_db(models.ExtractLog, OPAC_PROC_LOGS_DB_NAME):
            return models.ExtractLog.objects.order_by('-time')

    def do_delete_all(self):
        register_connections()
        with switch_db(models.ExtractLog, OPAC_PROC_LOGS_DB_NAME):
            models.ExtractLog.all().delete()
        flash('All records deleted successfully!', 'success')

    def do_delete_selected(self, ids):
        register_connections()
        with switch_db(models.ExtractLog, OPAC_PROC_LOGS_DB_NAME):
            models.ExtractLog.in_bulk(ids).delete()
        flash('%s records deleted successfully!' % len(ids), 'success')
