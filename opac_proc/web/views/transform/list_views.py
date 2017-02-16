# coding: utf-8
from mongoengine.context_managers import switch_db
from bson.objectid import ObjectId

from opac_proc.datastore import models
from opac_proc.web.views.generics.list_views import ListView
from opac_proc.datastore.mongodb_connector import register_connections, get_opac_logs_db_name
from opac_proc.transformers.process import TransformProcess
from opac_proc.web.helpers.list_generator import get_collection_list_view, get_journal_list_view, get_issue_list_view, \
    get_article_list_view, get_press_release_list_view, get_log_columns_list_view, get_log_filters_list_view

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
    list_columns = list_filters = get_collection_list_view()


class TransformJournalListView(TransformBaseListView):
    model_class = models.TransformJournal
    model_name = 'journal'
    page_title = "Transform: Journals"
    list_columns = list_filters = get_journal_list_view()


class TransformIssueListView(TransformBaseListView):
    model_class = models.TransformIssue
    model_name = 'issue'
    page_title = "Transform: Issues"
    list_columns = list_filters = get_issue_list_view()


class TransformArticleListView(TransformBaseListView):
    model_class = models.TransformArticle
    model_name = 'article'
    page_title = "Transform: Articles"
    list_columns = list_filters = get_article_list_view()


class TransformPressReleaseListView(TransformBaseListView):
    model_class = models.TransformPressRelease
    model_name = 'press_release'
    page_title = "Transform: Press Releases"
    list_columns = list_filters = get_press_release_list_view()


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
    list_columns = get_log_columns_list_view()
    list_filters = get_log_filters_list_view()

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
