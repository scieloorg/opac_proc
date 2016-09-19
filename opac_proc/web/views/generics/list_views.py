# coding: utf-8
from flask import render_template, flash, request
from flask.views import View
from flask_mongoengine import Pagination


class ListView(View):
    page_title = 'List view'
    page_subtitle = ''
    panel_title = ''
    template_name = 'object_list/base.html'
    per_page = 20
    list_colums = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update:',
            'field_name': 'updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Deleted?',
            'field_name': 'is_deleted',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Process completed?',
            'field_name': 'process_completed',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Must reprocess?',
            'field_name': 'must_reprocess',
            'field_type': 'boolean'
        },
    ]

    def render_template(self, context):
        return render_template(self.template_name, **context)

    def _pager_range(self, current_page, total_pages, span=10):
        prev_range = [x for x in range(current_page - span, current_page) if 0 < x < current_page]
        next_range = [x for x in range(current_page, current_page + span + 1) if current_page < x < total_pages]
        result_range = prev_range + [current_page] + next_range
        has_more_prevs = 1 < result_range[0] < current_page
        has_more_nexts = current_page < result_range[-1] < total_pages
        return {
            'has_more_prevs': has_more_prevs,   # tem mais paginas menores que o primeiro (menor) do result_range
            'has_more_nexts': has_more_nexts,   # tem mais paginas maiores que o ultimo (maior) do result_range
            'range': result_range
        }

    def dispatch_request(self):
        page = request.args.get('page', 1, type=int)
        objects = Pagination(self.get_objects(), page, self.per_page)
        context = {
            # meta:
            'page_title': self.page_title,
            'page_subtitle': self.page_subtitle,
            'panel_title': self.panel_title,
            'list_colums': self.list_colums,
            # objetos:
            'objects': objects.items,
            # paginas:
            'pager_range': self._pager_range(page, objects.pages),
            'current_page': page,
            'total_pages': objects.pages,
            'total_records': objects.total,
            'has_prev': objects.has_prev,
            'prev_num': objects.prev_num,
            'has_next': objects.has_next,
            'next_num': objects.next_num,
        }
        return self.render_template(context)
