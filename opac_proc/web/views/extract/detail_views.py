# coding: utf-8
from mongoengine.context_managers import switch_db
from opac_proc.datastore import models
from opac_proc.web.views.generics.detail_views import DetailView
from opac_proc.datastore.mongodb_connector import register_connections, get_opac_logs_db_name

OPAC_PROC_LOGS_DB_NAME = get_opac_logs_db_name()


class ExtractCollectionDetailView(DetailView):
    model_class = models.ExtractCollection
    page_title = u'Extract Collection Detail'


class ExtractJournalDetailView(DetailView):
    model_class = models.ExtractJournal
    page_title = u'Extract Journal Detail'


class ExtractIssueDetailView(DetailView):
    model_class = models.ExtractIssue
    page_title = u'Extract Issue Detail'


class ExtractArticleDetailView(DetailView):
    model_class = models.ExtractArticle
    page_title = u'Extract Article Detail'


class ExtractPressReleaseDetailView(DetailView):
    model_class = models.ExtractPressRelease
    page_title = u'Extract Press Release Detail'


class ExtractNewsDetailView(DetailView):
    model_class = models.ExtractNews
    page_title = u'Extract News Detail'


class ExtractLogDetailView(DetailView):
    model_class = models.ExtractLog
    page_title = u'Extract Log Detail'

    def get_document_by_id(self, object_id):
        """
        metodo que retorna o documento procurando pelo object_id.
        """
        register_connections()
        with switch_db(self.model_class, OPAC_PROC_LOGS_DB_NAME):
            return self.model_class.objects.get(id=object_id)
