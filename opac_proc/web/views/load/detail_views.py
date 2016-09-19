# coding: utf-8
from opac_proc.datastore import models
from opac_proc.web.views.generics.detail_views import DetailView


class LoadCollectionDetailView(DetailView):
    model_class = models.LoadCollection
    page_title = u'Load Collection Detail'


class LoadJournalDetailView(DetailView):
    model_class = models.LoadJournal
    page_title = u'Load Journal Detail'


class LoadIssueDetailView(DetailView):
    model_class = models.LoadIssue
    page_title = u'Load Journal Detail'


class LoadArticleDetailView(DetailView):
    model_class = models.LoadArticle
    page_title = u'Load Journal Detail'
