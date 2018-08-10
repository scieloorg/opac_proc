# coding: utf-8
from mongoengine.context_managers import switch_db
from bson.objectid import ObjectId

from opac_proc.datastore import models
from opac_proc.web.views.generics.list_views import ListView
from opac_proc.datastore.mongodb_connector import register_connections, get_opac_logs_db_name
from opac_proc.loaders.process import (
    ProcessLoadCollection,
    ProcessLoadJournal,
    ProcessLoadIssue,
    ProcessLoadArticle,
    ProcessLoadPressRelease,
    ProcessLoadNews
)

OPAC_PROC_LOGS_DB_NAME = get_opac_logs_db_name()


class LoadBaseListView(ListView):
    stage = 'load'
    can_process = True
    can_delete = True
    convert_pk_to_uuid = True


class LoadCollectionListView(LoadBaseListView):
    model_class = models.LoadCollection
    process_class = ProcessLoadCollection
    model_name = 'collection'
    page_title = "Load: Collection"
    list_columns = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'Acrônimo',
            'field_name': 'loaded_data.acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'Nome',
            'field_name': 'loaded_data.name',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update',
            'field_name': 'metadata.updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Process completed?',
            'field_name': 'metadata.process_completed',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Must reprocess?',
            'field_name': 'metadata.must_reprocess',
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
            'field_name': 'loaded_data.acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'Nome',
            'field_name': 'loaded_data.name',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update',
            'field_name': 'metadata.updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Process completed?',
            'field_name': 'metadata.process_completed',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Must reprocess?',
            'field_name': 'metadata.must_reprocess',
            'field_type': 'boolean'
        },
    ]


class LoadJournalListView(LoadBaseListView):
    model_class = models.LoadJournal
    process_class = ProcessLoadJournal
    model_name = 'journal'
    page_title = "Load: Journals"
    list_columns = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'Aconym',
            'field_name': 'loaded_data.acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'Print ISSN',
            'field_name': 'loaded_data.print_issn',
            'field_type': 'string'
        },
        {
            'field_label': u'SciELO ISSN',
            'field_name': 'loaded_data.scielo_issn',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update',
            'field_name': 'metadata.updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Process completed?',
            'field_name': 'metadata.process_completed',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Must reprocess?',
            'field_name': 'metadata.must_reprocess',
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
            'field_label': u'Aconym',
            'field_name': 'loaded_data.acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'Print ISSN',
            'field_name': 'loaded_data.print_issn',
            'field_type': 'string'
        },
        {
            'field_label': u'SciELO ISSN',
            'field_name': 'loaded_data.scielo_issn',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update',
            'field_name': 'metadata.updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Process completed?',
            'field_name': 'metadata.process_completed',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Must reprocess?',
            'field_name': 'metadata.must_reprocess',
            'field_type': 'boolean'
        },
    ]


class LoadIssueListView(LoadBaseListView):
    model_class = models.LoadIssue
    process_class = ProcessLoadIssue
    model_name = 'issue'
    page_title = "Load: Issues"
    list_columns = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'PID',
            'field_name': 'loaded_data.pid',
            'field_type': 'string'
        },
        {
            'field_label': u'Year',
            'field_name': 'loaded_data.year',
            'field_type': 'string'
        },
        {
            'field_label': u'Volume',
            'field_name': 'loaded_data.volume',
            'field_type': 'string'
        },
        {
            'field_label': u'Number',
            'field_name': 'loaded_data.number',
            'field_type': 'string'
        },
        {
            'field_label': u'Type',
            'field_name': 'loaded_data.type',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update',
            'field_name': 'metadata.updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Process completed?',
            'field_name': 'metadata.process_completed',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Reprocess?',
            'field_name': 'metadata.must_reprocess',
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
            'field_label': u'Aconym',
            'field_name': 'loaded_data.acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'Print ISSN',
            'field_name': 'loaded_data.print_issn',
            'field_type': 'string'
        },
        {
            'field_label': u'SciELO ISSN',
            'field_name': 'loaded_data.scielo_issn',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update',
            'field_name': 'metadata.updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Process completed?',
            'field_name': 'metadata.process_completed',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Must reprocess?',
            'field_name': 'metadata.must_reprocess',
            'field_type': 'boolean'
        },
    ]


class LoadArticleListView(LoadBaseListView):
    model_class = models.LoadArticle
    process_class = ProcessLoadArticle
    model_name = 'article'
    page_title = "Load: Articles"
    list_columns = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'PID',
            'field_name': 'loaded_data.pid',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update',
            'field_name': 'metadata.updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Process completed?',
            'field_name': 'metadata.process_completed',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Reprocess?',
            'field_name': 'metadata.must_reprocess',
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
            'field_name': 'loaded_data.pid',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update',
            'field_name': 'metadata.updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Process completed?',
            'field_name': 'metadata.process_completed',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Reprocess?',
            'field_name': 'metadata.must_reprocess',
            'field_type': 'boolean'
        },
    ]


class LoadPressReleaseListView(LoadBaseListView):
    model_class = models.LoadPressRelease
    process_class = ProcessLoadPressRelease
    model_name = 'press_release'
    page_title = "Load: Press Releases"


class LoadNewsListView(LoadBaseListView):
    model_class = models.LoadNews
    process_class = ProcessLoadNews
    model_name = 'news'
    page_title = "Load: News"


class LoadLogListView(LoadBaseListView):
    model_class = models.LoadLog
    model_name = 'loadlog'
    process_class = None  # logs somente tem o Delete
    can_process = False
    can_delete = True
    page_title = "Load: Logs"
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
            objects = super(LoadLogListView, self).get_objects()
            return objects.order_by('-time')

    def do_delete_all(self):
        register_connections()
        with switch_db(self.model_class, OPAC_PROC_LOGS_DB_NAME):
            super(LoadLogListView, self).do_delete_all()

    def do_delete_selected(self, ids):
        register_connections()
        with switch_db(self.model_class, OPAC_PROC_LOGS_DB_NAME):
            super(LoadLogListView, self).do_delete_selected(ids)

    def get_selected_ids(self):
        ids = super(LoadLogListView, self).get_selected_ids()
        return [ObjectId(_id.strip()) for _id in ids]
