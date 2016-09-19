# coding: utf-8
from opac_proc.datastore import models
from opac_proc.web.views.generics.detail_views import DetailView


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
