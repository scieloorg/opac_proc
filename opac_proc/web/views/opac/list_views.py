# coding: utf-8
from mongoengine.context_managers import switch_db
from opac_schema.v1 import models
from opac_proc.web.views.generics.list_views import ListView
from opac_proc.datastore.mongodb_connector import register_connections, get_opac_webapp_db_name

OPAC_WEBAPP_DB_NAME = get_opac_webapp_db_name()


class OpacBaseListView(ListView):
    stage = 'opac'
    can_process = False
    can_delete = True

    def get_objects(self):
        if self.model_class is None:
            raise ValueError("model class not defined")
        else:
            filters = self.get_filters()

        register_connections()
        with switch_db(self.model_class, OPAC_WEBAPP_DB_NAME):
            if self.list_filters and filters:
                return self.model_class.objects.filter(**filters)
            else:
                return self.model_class.objects()

    def do_delete_all(self):
        register_connections()
        with switch_db(self.model_class, OPAC_WEBAPP_DB_NAME):
            super(OpacBaseListView, self).do_delete_all()

    def do_delete_selected(self, ids):
        register_connections()
        with switch_db(self.model_class, OPAC_WEBAPP_DB_NAME):
            super(OpacBaseListView, self).do_delete_selected(ids)


class OpacCollectionListView(OpacBaseListView):
    model_class = models.Collection
    model_name = 'collection'
    page_title = "OPAC: Collections"
    list_columns = [
        {
            'field_label': u'ID',
            'field_name': '_id',
            'field_type': 'string'
        },
        {
            'field_label': u'Acrônimo',
            'field_name': 'acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'Nome',
            'field_name': 'name',
            'field_type': 'string'
        }
    ]
    list_filters = [
        {
            'field_label': u'ID',
            'field_name': '_id',
            'field_type': 'string'
        },
        {
            'field_label': u'Acrônimo',
            'field_name': 'acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'Nome',
            'field_name': 'name',
            'field_type': 'string'
        }
    ]


class OpacJournalListView(OpacBaseListView):
    model_class = models.Journal
    model_name = 'journal'
    page_title = "OPAC: Journals"
    list_columns = [
        {
            'field_label': u'ID',
            'field_name': '_id',
            'field_type': 'string'
        },
        {
            'field_label': u'Title',
            'field_name': 'title',
            'field_type': 'string'
        },
        {
            'field_label': u'Acrônimo',
            'field_name': 'acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'Scielo ISSN',
            'field_name': 'scielo_issn',
            'field_type': 'string'
        },
        {
            'field_label': u'Print ISSN',
            'field_name': 'print_issn',
            'field_type': 'string'
        },
        {
            'field_label': u'e-ISSN',
            'field_name': 'eletronic_issn',
            'field_type': 'string'
        }
    ]

    list_filters = [
        {
            'field_label': u'ID',
            'field_name': '_id',
            'field_type': 'string'
        },
        {
            'field_label': u'Title',
            'field_name': 'title',
            'field_type': 'string'
        },
        {
            'field_label': u'Acrônimo',
            'field_name': 'acronym',
            'field_type': 'string'
        },
        {
            'field_label': u'Scielo ISSN',
            'field_name': 'scielo_issn',
            'field_type': 'string'
        },
        {
            'field_label': u'Print ISSN',
            'field_name': 'print_issn',
            'field_type': 'string'
        },
        {
            'field_label': u'e-ISSN',
            'field_name': 'eletronic_issn',
            'field_type': 'string'
        }
    ]


class OpacIssueListView(OpacBaseListView):
    model_class = models.Issue
    model_name = 'issue'
    page_title = "OPAC: Issues"
    list_columns = [
        {
            'field_label': u'ID',
            'field_name': '_id',
            'field_type': 'string'
        },
        {
            'field_label': u'PID',
            'field_name': 'pid',
            'field_type': 'string'
        },
        {
            'field_label': u'Label',
            'field_name': 'label',
            'field_type': 'string'
        },
        {
            'field_label': u'Type',
            'field_name': 'type',
            'field_type': 'string'
        },
        {
            'field_label': u'Order',
            'field_name': 'order',
            'field_type': 'string'
        },
        {
            'field_label': u'Year',
            'field_name': 'year',
            'field_type': 'string'
        }
    ]

    list_filters = [
        {
            'field_label': u'ID',
            'field_name': '_id',
            'field_type': 'string'
        },
        {
            'field_label': u'PID',
            'field_name': 'pid',
            'field_type': 'string'
        },
        {
            'field_label': u'Label',
            'field_name': 'label',
            'field_type': 'string'
        },
        {
            'field_label': u'Type',
            'field_name': 'type',
            'field_type': 'string'
        },
        {
            'field_label': u'Order',
            'field_name': 'order',
            'field_type': 'string'
        },
        {
            'field_label': u'Year',
            'field_name': 'year',
            'field_type': 'string'
        }
    ]


class OpacArticleListView(OpacBaseListView):
    model_class = models.Article
    model_name = 'article'
    page_title = "OPAC: Articles"
    list_columns = [
        {
            'field_label': u'ID',
            'field_name': '_id',
            'field_type': 'string'
        },
        {
            'field_label': u'PID',
            'field_name': 'pid',
            'field_type': 'string'
        },
        {
            'field_label': u'Title',
            'field_name': 'title',
            'field_type': 'string'
        },
        {
            'field_label': u'Is Public?',
            'field_name': 'is_public',
            'field_type': 'boolean'
        }
    ]

    list_filters = [
        {
            'field_label': u'ID',
            'field_name': '_id',
            'field_type': 'string'
        },
        {
            'field_label': u'PID',
            'field_name': 'pid',
            'field_type': 'string'
        },
        {
            'field_label': u'Title',
            'field_name': 'title',
            'field_type': 'string'
        },
        {
            'field_label': u'Is Public?',
            'field_name': 'is_public',
            'field_type': 'boolean'
        }
    ]


class OpacSponsorListView(OpacBaseListView):
    model_class = models.Sponsor
    model_name = 'sponsor'
    page_title = "OPAC: Sponsors"
    list_columns = [
        {
            'field_label': u'ID',
            'field_name': '_id',
            'field_type': 'string'
        },
        {
            'field_label': u'Name',
            'field_name': 'name',
            'field_type': 'string'
        },
        {
            'field_label': u'URL',
            'field_name': 'url',
            'field_type': 'string'
        }
    ]

    list_filters = [
        {
            'field_label': u'ID',
            'field_name': '_id',
            'field_type': 'string'
        },
        {
            'field_label': u'Name',
            'field_name': 'name',
            'field_type': 'string'
        },
        {
            'field_label': u'URL',
            'field_name': 'url',
            'field_type': 'string'
        }
    ]


class OpacPageListView(OpacBaseListView):
    model_class = models.Pages
    model_name = 'page'
    page_title = "OPAC: Pages"
    list_columns = [
        {
            'field_label': u'ID',
            'field_name': '_id',
            'field_type': 'string'
        },
        {
            'field_label': u'Name',
            'field_name': 'name',
            'field_type': 'string'
        },
        {
            'field_label': u'Language',
            'field_name': 'language',
            'field_type': 'string'
        },
        {
            'field_label': u'Journal',
            'field_name': 'journal',
            'field_type': 'string'
        }
    ]

    list_filters = [
        {
            'field_label': u'ID',
            'field_name': '_id',
            'field_type': 'string'
        },
        {
            'field_label': u'Name',
            'field_name': 'name',
            'field_type': 'string'
        },
        {
            'field_label': u'Language',
            'field_name': 'language',
            'field_type': 'string'
        },
        {
            'field_label': u'Journal',
            'field_name': 'journal',
            'field_type': 'string'
        }
    ]


class OpacPressReleaseListView(OpacBaseListView):
    model_class = models.PressRelease
    model_name = 'PressRelease'
    page_title = "OPAC: Press Release"
    list_columns = [
        {
            'field_label': u'ID',
            'field_name': '_id',
            'field_type': 'string'
        },
        {
            'field_label': u'Language',
            'field_name': 'language',
            'field_type': 'string'
        },
        {
            'field_label': u'URL',
            'field_name': 'url',
            'field_type': 'string'
        },
        {
            'field_label': u'Publication Date',
            'field_name': 'publication_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Created',
            'field_name': 'created',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Updated',
            'field_name': 'updated',
            'field_type': 'date_time'
        },
    ]

    list_filters = [
        {
            'field_label': u'ID',
            'field_name': '_id',
            'field_type': 'string'
        },
        {
            'field_label': u'Language',
            'field_name': 'language',
            'field_type': 'string'
        },
        {
            'field_label': u'URL',
            'field_name': 'url',
            'field_type': 'string'
        },
        {
            'field_label': u'Publication Date',
            'field_name': 'publication_date',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Created',
            'field_name': 'created',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Updated',
            'field_name': 'updated',
            'field_type': 'date_time'
        },
    ]


class OpacNewsListView(OpacBaseListView):
    model_class = models.News
    model_name = 'News'
    page_title = "OPAC: News"
    list_columns = [
        {
            'field_label': u'ID',
            'field_name': '_id',
            'field_type': 'string'
        },
        {
            'field_label': u'URL',
            'field_name': 'url',
            'field_type': 'string'
        },
        {
            'field_label': u'Pub. Date',
            'field_name': 'publication_date',
            'field_type': 'string'
        },
        {
            'field_label': u'Title',
            'field_name': 'title',
            'field_type': 'string'
        },
        {
            'field_label': u'Language',
            'field_name': 'language',
            'field_type': 'string'
        },
        {
            'field_label': u'Public?',
            'field_name': 'is_public',
            'field_type': 'boolean'
        }
    ]

    list_filters = [
        {
            'field_label': u'ID',
            'field_name': '_id',
            'field_type': 'string'
        },
        {
            'field_label': u'URL',
            'field_name': 'url',
            'field_type': 'string'
        },
        {
            'field_label': u'Pub. Date',
            'field_name': 'publication_date',
            'field_type': 'string'
        },
        {
            'field_label': u'Title',
            'field_name': 'title',
            'field_type': 'string'
        },
        {
            'field_label': u'Language',
            'field_name': 'language',
            'field_type': 'string'
        },
        {
            'field_label': u'Public?',
            'field_name': 'is_public',
            'field_type': 'boolean'
        }
    ]
