# coding: utf-8
from mongoengine.context_managers import switch_db
from opac_schema.v1 import models
from opac_proc.web.views.generics.detail_views import DetailView
from opac_proc.datastore.mongodb_connector import register_connections, get_opac_webapp_db_name

OPAC_WEBAPP_DB_NAME = get_opac_webapp_db_name()


class OpacBaseDetailView(DetailView):

    def get_document_by_id(self, object_id):
        """
        metodo que retorna o documento procurando pelo object_id.
        """
        register_connections()
        with switch_db(self.model_class, OPAC_WEBAPP_DB_NAME):
            return self.model_class.objects.get(_id=object_id)


class OpacCollectionDetailView(OpacBaseDetailView):
    model_class = models.Collection
    page_title = u'OPAC Collection Detail'


class OpacJournalDetailView(OpacBaseDetailView):
    model_class = models.Journal
    page_title = u'OPAC Journal Detail'


class OpacIssueDetailView(OpacBaseDetailView):
    model_class = models.Issue
    page_title = u'OPAC Issue Detail'


class OpacArticleDetailView(OpacBaseDetailView):
    model_class = models.Article
    page_title = u'OPAC Article Detail'


class OpacSponsorDetailView(OpacBaseDetailView):
    model_class = models.Sponsor
    page_title = u'OPAC Sponsor Detail'


class OpacPageDetailView(OpacBaseDetailView):
    model_class = models.Pages
    page_title = u'OPAC Pages Detail'


class OpacResourceDetailView(OpacBaseDetailView):
    model_class = models.Resource
    page_title = u'OPAC Resource Detail'


class OpacPressReleaseDetailView(OpacBaseDetailView):
    model_class = models.PressRelease
    page_title = u'OPAC Press Release Detail'


class OpacNewsDetailView(OpacBaseDetailView):
    model_class = models.News
    page_title = u'OPAC News Detail'
