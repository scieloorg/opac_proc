# coding: utf-8
import traceback
from mongoengine.context_managers import switch_db
from bson.objectid import ObjectId
from flask import flash
from opac_proc.datastore import models
from opac_proc.web.views.generics.list_views import ListView
from opac_proc.datastore.mongodb_connector import register_connections, get_opac_logs_db_name
from opac_proc.transformers.process import (
    ProcessTransformCollection,
    ProcessTransformJournal,
    ProcessTransformIssue,
    ProcessTransformArticle,
    ProcessTransformPressRelease,
    ProcessTransformNews
)

OPAC_PROC_LOGS_DB_NAME = get_opac_logs_db_name()


class TransformBaseListView(ListView):
    stage = 'transform'
    can_create = True
    can_update = True
    can_delete = True


class TransformCollectionListView(TransformBaseListView):
    model_class = models.TransformCollection
    process_class = ProcessTransformCollection
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
    process_class = ProcessTransformJournal
    model_name = 'journal'
    page_title = "Transform: Journals"
    list_columns = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'Acronym',
            'field_name': 'acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'P-ISSN',
            'field_name': 'print_issn',
            'field_type': 'string'
        },
        {
            'field_label': u'E-ISSN',
            'field_name': 'eletronic_issn',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update:',
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

    list_filters = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'uuid'
        },
        {
            'field_label': u'Acronym',
            'field_name': 'acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'P-ISSN',
            'field_name': 'print_issn',
            'field_type': 'string'
        },
        {
            'field_label': u'E-ISSN',
            'field_name': 'eletronic_issn',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update:',
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


class TransformIssueListView(TransformBaseListView):
    model_class = models.TransformIssue
    process_class = ProcessTransformIssue
    model_name = 'issue'
    page_title = "Transform: Issues"
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
            'field_label': u'Label',
            'field_name': 'label',
            'field_type': 'string'
        },
        {
            'field_label': u'Type',
            'field_name': 'type',
            'field_type': 'string'
        },
        {
            'field_label': u'Suppl Text',
            'field_name': 'suppl_text',
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
            'field_label': u'Label',
            'field_name': 'label',
            'field_type': 'string'
        },
        {
            'field_label': u'Type',
            'field_name': 'type',
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
            'field_label': u'Reprocess?',
            'field_name': 'must_reprocess',
            'field_type': 'boolean'
        },
    ]


class TransformArticleListView(TransformBaseListView):
    model_class = models.TransformArticle
    process_class = ProcessTransformArticle
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
            'field_label': u'Versão (xml/html)',
            'field_name': 'data_model_version',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update:',
            'field_name': 'updated_at',
            'field_type': 'date_time'
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
            'field_label': u'Versão (xml/html)',
            'field_name': 'data_model_version',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update:',
            'field_name': 'updated_at',
            'field_type': 'date_time'
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

    custom_actions = [
        {
            'method_name': 'do_reprocess_xml_only',    # nome de função python que implementa a ação
            'label': 'Reprocessar XMLs',             # nome da ação para mostrar pro usuário
            'icon_class': 'fa fa-refresh',     # class CSS para o icone. ex: 'fa fa-gear'
            'can_select_rows': False,        # boolean, se permite ou não a opção "All/Selected" ou não
        },
    ]

    def do_reprocess_xml_only(self):
        def chunks(l, n):
            """Yield successive n-sized chunks from l."""
            for i in range(0, len(l), n):
                yield l[i:i + n]

        processor = self.process_class()
        list_of_all_ids = self.model_class.objects.filter(data_model_version='xml').values_list('_id')
        SLICE_SIZE = 1000
        count_xml_articles = len(list_of_all_ids)
        try:
            if len(list_of_all_ids) <= SLICE_SIZE:
                id_as_string_list = [str(_id) for _id in list_of_all_ids]
                processor.update(id_as_string_list)
            else:
                list_of_list_of_ids = list(chunks(list_of_all_ids, SLICE_SIZE))
                for list_of_ids in list_of_list_of_ids:
                    id_as_string_list = [str(_id) for _id in list_of_ids]
                    processor.update(id_as_string_list)

        except Exception as e:
            traceback_str = traceback.format_exc()
            self._trigger_messages(is_error=True, exception_obj=e, traceback_str=traceback_str, items_count=count_xml_articles)
        else:
            self._trigger_messages(items_count=count_xml_articles)


class TransformPressReleaseListView(TransformBaseListView):
    model_class = models.TransformPressRelease
    process_class = ProcessTransformPressRelease
    model_name = 'press_release'
    page_title = "Transform: Press Releases"
    list_columns = [
        {
            'field_label': u'Journal',
            'field_name': 'journal_acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'URL',
            'field_name': 'url',
            'field_type': 'string'
        },
        {
            'field_label': u'Published',
            'field_name': 'publication_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Language',
            'field_name': 'language',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update:',
            'field_name': 'updated_at',
            'field_type': 'date_time'
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
            'field_label': u'Journal',
            'field_name': 'journal_acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'URL',
            'field_name': 'url',
            'field_type': 'string'
        },
        {
            'field_label': u'Published',
            'field_name': 'publication_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Language',
            'field_name': 'language',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update:',
            'field_name': 'updated_at',
            'field_type': 'date_time'
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


class TransformNewsListView(TransformBaseListView):
    model_class = models.TransformNews
    process_class = ProcessTransformNews
    model_name = 'news'
    page_title = "Transform: News"
    list_columns = [
        {
            'field_label': u'URL',
            'field_name': 'url',
            'field_type': 'string'
        },
        {
            'field_label': u'Published',
            'field_name': 'publication_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Language',
            'field_name': 'language',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update:',
            'field_name': 'updated_at',
            'field_type': 'date_time'
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
            'field_label': u'URL',
            'field_name': 'url',
            'field_type': 'string'
        },
        {
            'field_label': u'Published',
            'field_name': 'publication_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Language',
            'field_name': 'language',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update:',
            'field_name': 'updated_at',
            'field_type': 'date_time'
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
