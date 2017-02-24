# coding: utf-8
from mongoengine.context_managers import switch_db
from opac_proc.datastore import models
from opac_proc.web.views.generics.detail_views import DetailView
from opac_proc.datastore.mongodb_connector import register_connections, get_opac_logs_db_name

OPAC_PROC_LOGS_DB_NAME = get_opac_logs_db_name()


class TransformCollectionDetailView(DetailView):
    model_class = models.TransformCollection
    page_title = u'Transform Collection Detail'


class TransformJournalDetailView(DetailView):
    model_class = models.TransformJournal
    page_title = u'Transform Journal Detail'


class TransformIssueDetailView(DetailView):
    model_class = models.TransformIssue
    page_title = u'Transform Issue Detail'


class TransformArticleDetailView(DetailView):
    model_class = models.TransformArticle
    page_title = u'Transform Article Detail'


class TransformPressReleaseDetailView(DetailView):
    model_class = models.TransformPressRelease
    page_title = u'Transform Press Release Detail'


class TransformLogDetailView(DetailView):
    model_class = models.TransformLog
    page_title = u'Transform Log Detail'

    def get_document_by_id(self, object_id):
        """
        metodo que retorna o documento procurando pelo object_id.
        """
        register_connections()
        with switch_db(self.model_class, OPAC_PROC_LOGS_DB_NAME):
            return self.model_class.objects.get(id=object_id)
