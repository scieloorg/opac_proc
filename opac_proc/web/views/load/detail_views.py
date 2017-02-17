# coding: utf-8
from mongoengine.context_managers import switch_db
from opac_proc.datastore import models
from opac_proc.web.views.generics.detail_views import DetailView
from opac_proc.datastore.mongodb_connector import register_connections, get_opac_logs_db_name

OPAC_PROC_LOGS_DB_NAME = get_opac_logs_db_name()


class LoadCollectionDetailView(DetailView):
    model_class = models.LoadCollection
    page_title = u'Load Collection Detail'


class LoadJournalDetailView(DetailView):
    model_class = models.LoadJournal
    page_title = u'Load Journal Detail'


class LoadIssueDetailView(DetailView):
    model_class = models.LoadIssue
    page_title = u'Load Issue Detail'


class LoadArticleDetailView(DetailView):
    model_class = models.LoadArticle
    page_title = u'Load Article Detail'


class LoadPressReleaseDetailView(DetailView):
    model_class = models.LoadPressRelease
    page_title = u'Load PressRelease Detail'


class LoadLogDetailView(DetailView):
    model_class = models.LoadLog
    page_title = u'Load Log Detail'

    def get_document_by_id(self, object_id):
        """
        metodo que retorna o documento procurando pelo object_id.
        """
        register_connections()
        with switch_db(self.model_class, OPAC_PROC_LOGS_DB_NAME):
            return self.model_class.objects.get(id=object_id)
