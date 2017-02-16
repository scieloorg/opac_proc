# coding: utf-8
from mongoengine.context_managers import switch_db
from bson.objectid import ObjectId

from opac_proc.datastore import models
from opac_proc.web.helpers.list_generator import get_collection_list_view, get_journal_list_view, get_issue_list_view, \
    get_article_list_view, get_press_release_list_view, get_log_columns_list_view, get_log_filters_list_view
from opac_proc.web.views.generics.list_views import ListView
from opac_proc.datastore.mongodb_connector import register_connections, get_opac_logs_db_name
from opac_proc.extractors.process import ExtractProcess

OPAC_PROC_LOGS_DB_NAME = get_opac_logs_db_name()


class ExtractBaseListView(ListView):
    stage = 'extract'
    process_class = ExtractProcess
    can_create = True
    can_update = True
    can_delete = True


class ExtractCollectionListView(ExtractBaseListView):
    model_class = models.ExtractCollection
    model_name = 'collection'
    page_title = "Extract: Collection"
    list_columns = list_filters = get_collection_list_view()


class ExtractJournalListView(ExtractBaseListView):
    model_class = models.ExtractJournal
    model_name = 'journal'
    page_title = "Extract: Journals"
    list_columns = list_filters = get_journal_list_view()


class ExtractIssueListView(ExtractBaseListView):
    model_class = models.ExtractIssue
    model_name = 'issue'
    page_title = "Extract: Issues"
    list_columns = list_filters = get_issue_list_view()


class ExtractArticleListView(ExtractBaseListView):
    model_class = models.ExtractArticle
    model_name = 'article'
    page_title = "Extract: Articles"
    list_columns = list_filters = get_article_list_view()


class ExtractPressReleaseListView(ExtractBaseListView):
    model_class = models.ExtractPressRelease
    model_name = 'press_release'
    page_title = "Extract: Press Releases"
    list_columns = list_filters = get_press_release_list_view()


class ExtractLogListView(ExtractBaseListView):
    model_class = models.ExtractLog
    model_name = 'loadlog'
    process_class = None  # logs somente tem o Delete
    can_create = False
    can_update = False
    can_delete = True
    page_title = "Extract: Logs"
    page_subtitle = "most recent first"
    per_page = 50
    list_columns = get_log_columns_list_view()
    list_filters = get_log_filters_list_view()

    def get_objects(self):
        register_connections()
        with switch_db(self.model_class, OPAC_PROC_LOGS_DB_NAME):
            objects = super(ExtractLogListView, self).get_objects()
            return objects.order_by('-time')

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
        return [ObjectId(_id.strip()) for _id in ids]
