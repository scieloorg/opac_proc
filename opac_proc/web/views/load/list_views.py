# coding: utf-8
from mongoengine.context_managers import switch_db
from bson.objectid import ObjectId

from opac_proc.datastore import models
from opac_proc.web.helpers.list_generator import get_collection_list_view, get_journal_list_view, get_issue_list_view, \
    get_article_list_view, get_log_columns_list_view, get_log_filters_list_view, get_press_release_list_view
from opac_proc.web.views.generics.list_views import ListView
from opac_proc.datastore.mongodb_connector import register_connections, get_opac_logs_db_name
from opac_proc.loaders.process import LoadProcess

OPAC_PROC_LOGS_DB_NAME = get_opac_logs_db_name()


class LoadBaseListView(ListView):
    stage = 'load'
    process_class = LoadProcess
    can_create = True
    can_update = True
    can_delete = True


class LoadCollectionListView(LoadBaseListView):
    model_class = models.LoadCollection
    model_name = 'collection'
    page_title = "Load: Collection"
    list_columns = list_filters = get_collection_list_view()


class LoadJournalListView(LoadBaseListView):
    model_class = models.LoadJournal
    model_name = 'journal'
    page_title = "Load: Journals"
    list_columns = list_filters = get_journal_list_view()


class LoadIssueListView(LoadBaseListView):
    model_class = models.LoadIssue
    model_name = 'issue'
    page_title = "Load: Issues"
    list_columns = list_filters = get_issue_list_view()


class LoadArticleListView(LoadBaseListView):
    model_class = models.LoadArticle
    model_name = 'article'
    page_title = "Load: Articles"
    list_columns = list_filters = get_article_list_view()


class LoadPressReleaseListView(LoadBaseListView):
    model_class = models.LoadArticle
    model_name = 'Press Release'
    page_title = "Load: Press Releases"
    list_columns = list_filters = get_press_release_list_view()


class LoadLogListView(LoadBaseListView):
    model_class = models.LoadLog
    model_name = 'loadlog'
    process_class = None  # logs somente tem o Delete
    can_create = False
    can_update = False
    can_delete = True
    page_title = "Load: Logs"
    page_subtitle = "most recent first"
    per_page = 50
    list_columns = get_log_columns_list_view()
    list_filters = get_log_filters_list_view()

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
