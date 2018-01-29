# coding: utf-8
from opac_proc.datastore import identifiers_models
from opac_proc.web.views.generics.detail_views import DetailView


class IdentifiersCollectionDetailView(DetailView):
    model_class = identifiers_models.CollectionIdModel
    page_title = u'IDs Collection Detail'
    template_name = 'object_detail/source_sync/detail_view.html'


class IdentifiersJournalDetailView(DetailView):
    model_class = identifiers_models.JournalIdModel
    page_title = u'IDs Journal Detail'
    template_name = 'object_detail/source_sync/detail_view.html'


class IdentifiersIssueDetailView(DetailView):
    model_class = identifiers_models.IssueIdModel
    page_title = u'IDs Issue Detail'
    template_name = 'object_detail/source_sync/detail_view.html'


class IdentifiersArticleDetailView(DetailView):
    model_class = identifiers_models.ArticleIdModel
    page_title = u'IDs Article Detail'
    template_name = 'object_detail/source_sync/detail_view.html'


class IdentifiersPressReleaseDetailView(DetailView):
    model_class = identifiers_models.PressReleaseIdModel
    page_title = u'IDs Press Release Detail'
    template_name = 'object_detail/source_sync/detail_view.html'


class IdentifiersNewsDetailView(DetailView):
    model_class = identifiers_models.NewsIdModel
    page_title = u'IDs News Detail'
    template_name = 'object_detail/source_sync/detail_view.html'
