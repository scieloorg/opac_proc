# coding: utf-8
from bson.objectid import ObjectId
from opac_proc.datastore import models
from opac_proc.web.views.generics.list_views import ListView


class MessageListView(ListView):
    stage = 'default'
    can_process = False
    can_delete = True
    model_class = models.Message
    model_name = 'message'
    page_title = "List: Messages"
    list_columns = [
        {
            'field_label': u'Assunto',
            'field_name': 'subject',
            'field_type': 'string'
        },
        {
            'field_label': u'Tipo',
            'field_name': 'msg_type',
            'field_type': 'string'
        },
        {
            'field_label': u'Fase',
            'field_name': 'stage',
            'field_type': 'string'
        },
        {
            'field_label': u'Modelo',
            'field_name': 'model_name',
            'field_type': 'string'
        },
        {
            'field_label': u'Não lida?',
            'field_name': 'unread',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Data de criação',
            'field_name': 'created_at',
            'field_type': 'date_time'
        },
    ]

    list_filters = [
        {
            'field_label': u'Assunto',
            'field_name': 'subject',
            'field_type': 'string'
        },
        {
            'field_label': u'Tipo',
            'field_name': 'msg_type',
            'field_type': 'string'
        },
        {
            'field_label': u'Fase',
            'field_name': 'stage',
            'field_type': 'string'
        },
        {
            'field_label': u'Modelo',
            'field_name': 'model_name',
            'field_type': 'string'
        },
        {
            'field_label': u'Não lida?',
            'field_name': 'unread',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Data de criação',
            'field_name': 'created_at',
            'field_type': 'date_time'
        },
    ]

    def get_selected_ids(self, *args, **kwargs):
        ids = super(MessageListView, self).get_selected_ids()
        return [ObjectId(_id.strip()) for _id in ids]
