# coding: utf-8
from opac_proc.datastore import models
from opac_proc.web.views.generics.detail_views import DetailView


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
