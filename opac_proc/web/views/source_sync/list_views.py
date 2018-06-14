# coding: utf-8

from opac_proc.datastore import identifiers_models
from opac_proc.web.views.generics.list_views import ListView


class IdentifiersBaseListView(ListView):
    stage = 'sync_ids'
    can_process = False
    can_delete = False


class IdentifiersCollectionListView(IdentifiersBaseListView):
    model_class = identifiers_models.CollectionIdModel
    model_name = 'collection'
    page_title = "Identifiers: Collection"
    list_columns = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'Acrônimo',
            'field_name': 'collection_acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'Criação',
            'field_name': 'created_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Atualização',
            'field_name': 'updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Processing Date',
            'field_name': 'processing_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Extração',
            'field_name': 'extract_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Transformação',
            'field_name': 'transform_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Carga',
            'field_name': 'load_execution_date',
            'field_type': 'date_time'
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
            'field_name': 'collection_acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'Criação',
            'field_name': 'created_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Atualização',
            'field_name': 'updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Processing Date',
            'field_name': 'processing_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Extração',
            'field_name': 'extract_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Transformação',
            'field_name': 'transform_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Carga',
            'field_name': 'load_execution_date',
            'field_type': 'date_time'
        },
    ]


class IdentifiersJournalListView(IdentifiersBaseListView):
    model_class = identifiers_models.JournalIdModel
    model_name = 'journal'
    page_title = "Identifiers: Journals"
    list_columns = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'Coleção',
            'field_name': 'collection_acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'ISSN',
            'field_name': 'journal_issn',
            'field_type': 'string'
        },
        {
            'field_label': u'Criação',
            'field_name': 'created_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Atualização',
            'field_name': 'updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Processing Date',
            'field_name': 'processing_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Extração',
            'field_name': 'extract_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Transformação',
            'field_name': 'transform_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Carga',
            'field_name': 'load_execution_date',
            'field_type': 'date_time'
        },
    ]

    list_filters = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'uuid'
        },
        {
            'field_label': u'Coleção',
            'field_name': 'collection_acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'Criação',
            'field_name': 'created_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Atualização',
            'field_name': 'updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Processing Date',
            'field_name': 'processing_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Extração',
            'field_name': 'extract_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Transformação',
            'field_name': 'transform_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Carga',
            'field_name': 'load_execution_date',
            'field_type': 'date_time'
        },
    ]


class IdentifiersIssueListView(IdentifiersBaseListView):
    model_class = identifiers_models.IssueIdModel
    model_name = 'issue'
    page_title = "Identifiers: Issues"
    list_columns = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'Coleção',
            'field_name': 'collection_acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'ISSN',
            'field_name': 'journal_issn',
            'field_type': 'string'
        },
        {
            'field_label': u'Issue PID',
            'field_name': 'issue_pid',
            'field_type': 'string'
        },
        {
            'field_label': u'Criação',
            'field_name': 'created_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Atualização',
            'field_name': 'updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Processing Date',
            'field_name': 'processing_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Extração',
            'field_name': 'extract_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Transformação',
            'field_name': 'transform_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Carga',
            'field_name': 'load_execution_date',
            'field_type': 'date_time'
        },
    ]

    list_filters = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'uuid'
        },
        {
            'field_label': u'Coleção',
            'field_name': 'collection_acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'Criação',
            'field_name': 'created_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Atualização',
            'field_name': 'updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Processing Date',
            'field_name': 'processing_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Extração',
            'field_name': 'extract_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Transformação',
            'field_name': 'transform_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Carga',
            'field_name': 'load_execution_date',
            'field_type': 'date_time'
        },
    ]


class IdentifiersArticleListView(IdentifiersBaseListView):
    model_class = identifiers_models.ArticleIdModel
    model_name = 'article'
    page_title = "Identifiers: Articles"
    list_columns = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'Coleção',
            'field_name': 'collection_acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'ISSN',
            'field_name': 'journal_issn',
            'field_type': 'string'
        },
        {
            'field_label': u'Issue PID',
            'field_name': 'issue_pid',
            'field_type': 'string'
        },
        {
            'field_label': u'Article PID',
            'field_name': 'article_pid',
            'field_type': 'string'
        },
        {
            'field_label': u'Criação',
            'field_name': 'created_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Atualização',
            'field_name': 'updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Processing Date',
            'field_name': 'processing_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Extração',
            'field_name': 'extract_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Transformação',
            'field_name': 'transform_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Carga',
            'field_name': 'load_execution_date',
            'field_type': 'date_time'
        },
    ]

    list_filters = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'uuid'
        },
        {
            'field_label': u'Coleção',
            'field_name': 'collection_acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'Criação',
            'field_name': 'created_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Atualização',
            'field_name': 'updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Processing Date',
            'field_name': 'processing_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Extração',
            'field_name': 'extract_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Transformação',
            'field_name': 'transform_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Carga',
            'field_name': 'load_execution_date',
            'field_type': 'date_time'
        },
    ]


class IdentifiersPressReleaseListView(IdentifiersBaseListView):
    model_class = identifiers_models.PressReleaseIdModel
    model_name = 'press_release'
    page_title = "Identifiers: Press Releases"

    list_columns = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'Coleção',
            'field_name': 'collection_acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'URL Id',
            'field_name': 'url_id',
            'field_type': 'string'
        },
        {
            'field_label': u'Criação',
            'field_name': 'created_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Atualização',
            'field_name': 'updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Processing Date',
            'field_name': 'processing_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Extração',
            'field_name': 'extract_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Transformação',
            'field_name': 'transform_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Carga',
            'field_name': 'load_execution_date',
            'field_type': 'date_time'
        },
    ]

    list_filters = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'uuid'
        },
        {
            'field_label': u'Coleção',
            'field_name': 'collection_acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'URL Id',
            'field_name': 'url_id',
            'field_type': 'string'
        },
        {
            'field_label': u'Criação',
            'field_name': 'created_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Atualização',
            'field_name': 'updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Processing Date',
            'field_name': 'processing_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Extração',
            'field_name': 'extract_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Transformação',
            'field_name': 'transform_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Carga',
            'field_name': 'load_execution_date',
            'field_type': 'date_time'
        },
    ]


class IdentifiersNewsListView(IdentifiersBaseListView):
    model_class = identifiers_models.NewsIdModel
    model_name = 'news'
    page_title = "Identifiers: News"

    list_columns = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'Coleção',
            'field_name': 'collection_acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'URL Id',
            'field_name': 'url_id',
            'field_type': 'string'
        },
        {
            'field_label': u'Criação',
            'field_name': 'created_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Atualização',
            'field_name': 'updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Processing Date',
            'field_name': 'processing_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Extração',
            'field_name': 'extract_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Transformação',
            'field_name': 'transform_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Carga',
            'field_name': 'load_execution_date',
            'field_type': 'date_time'
        },
    ]

    list_filters = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'uuid'
        },
        {
            'field_label': u'Coleção',
            'field_name': 'collection_acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'URL Id',
            'field_name': 'url_id',
            'field_type': 'string'
        },
        {
            'field_label': u'Criação',
            'field_name': 'created_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Atualização',
            'field_name': 'updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Processing Date',
            'field_name': 'processing_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Extração',
            'field_name': 'extract_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Transformação',
            'field_name': 'transform_execution_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Data Carga',
            'field_name': 'load_execution_date',
            'field_type': 'date_time'
        },
    ]
