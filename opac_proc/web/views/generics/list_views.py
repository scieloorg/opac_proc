# coding: utf-8
from flask import render_template, flash, request, redirect, jsonify
from flask.views import View
from flask_mongoengine import Pagination


class ListView(View):
    methods = ['GET', 'POST']
    stage = ''  # 'extract' | 'transform' | 'load'
    model_class = None  # classe do modelo. Ex: LoadCollection, TransformJournal
    model_name = ''  # nome do modelo (lowercase). ex: "article" ou "issue" ou "journal" ou "collection"
    process_class = None  # subclasse de Process que vai atender a ação
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

    can_create = False
    can_update = False
    can_delete = False

    _allowed_POST_action_names = [
        'create',
        'update_all',
        'update_selected',
        'delete_all',
        'delete_selected'
    ]

    def get_objects(self):
        if self.model_class is None:
            raise ValueError("model class not defined")
        else:
            return self.model_class.objects()

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

    def do_create(self):
        processor = self.process_class()
        if self.model_name == 'collection':
            processor.process_all_collections()
        elif self.model_name == 'journal':
            processor.process_all_journals()
        elif self.model_name == 'issue':
            processor.process_all_issues()
        elif self.model_name == 'article':
            processor.process_all_articles()
        else:
            raise ValueError('Invalid "model_name" attribute')
        flash("Started process to %s all %s(s)" % (self.stage, self.model_name))

    def do_update_all(self):
        processor = self.process_class()
        if self.model_name == 'collection':
            processor.reprocess_collections()
        elif self.model_name == 'journal':
            processor.reprocess_journals()
        elif self.model_name == 'issue':
            processor.reprocess_issues()
        elif self.model_name == 'article':
            processor.reprocess_articles()
        else:
            raise ValueError('Invalid "model_name" attribute')

        flash("Started reprocess to %s all %s" % (self.stage.upper(), self.model_name.upper()))

    def do_update_selected(self, ids):
        processor = self.process_class()
        if self.model_name == 'collection':
            processor.reprocess_collections(ids)
        elif self.model_name == 'journal':
            processor.reprocess_journals(ids)
        elif self.model_name == 'issue':
            processor.reprocess_issues(ids)
        elif self.model_name == 'article':
            processor.reprocess_articles(ids)
        else:
            raise ValueError('Invalid "model_name" attribute')

        flash("Started reprocess to %s %s %s" % (self.stage.upper(), len(ids), self.model_name.upper()))

    def do_delete_all(self):
        if self.model_class is None:
            raise ValueError("model class not defined")
        else:
            self.model_class.objects.all().delete()
            flash("All records deleted successfully!", "success")

    def do_delete_selected(self, ids):
        if self.model_class is None:
            raise ValueError("model class not defined")

        delete_errors_count = 0
        for oid in ids:
            try:
                model = self.model_class.objects.get(pk=oid)
                model.delete()
            except Exception as e:
                delete_errors_count += 1
        if delete_errors_count:
            flash("%s records cannot be deleted" % delete_errors_count, "error")
        successfully_deleted = len(ids) - delete_errors_count
        if successfully_deleted > 0:
            flash("%s records deleted successfully!" % successfully_deleted, "success")
        else:
            flash("%s records deleted successfully!" % successfully_deleted, "warning")

    def get_selected_ids(self):
        ids = request.form.getlist('rowid')
        if not ids:
            raise ValueError("No records selected")
        elif isinstance(ids, list):
            ids = [id.strip() for id in ids]
        else:
            raise ValueError("Invalid selection %s" % ids)
        return ids

    def dispatch_request(self):
        if request.method == 'POST':  # create action
            action_name = request.form['action_name']
            if action_name not in self._allowed_POST_action_names:
                flask(u'Invalid operation: %s' % action_name)
            else:
                if action_name == 'create':
                    if self.can_create:
                        try:
                            self.do_create()
                        except Exception as e:
                            flash(u'ERROR: %s' % str(e), 'error')
                    else:
                        flash(u'This action is disabled', 'error')
                elif action_name == 'update_all':
                    if self.can_update:
                        try:
                            self.do_update_all()
                        except Exception as e:
                            flash(u'ERROR: %s' % str(e), 'error')
                    else:
                        flash(u'This action is disabled', 'error')
                elif action_name == 'update_selected':
                    if self.can_update:
                        try:
                            ids = self.get_selected_ids()
                            if ids:
                                self.do_update_selected(ids)
                            else:
                                flask(u'Invalid selection', 'error')
                        except Exception as e:
                            flash(u'ERROR: %s' % str(e), 'error')
                    else:
                        flash(u'This action is disabled', 'error')
                elif action_name == 'delete_all':
                    if self.can_delete:
                        try:
                            self.do_delete_all()
                        except Exception as e:
                            flash(u'ERROR: %s' % str(e), 'error')
                    else:
                        flash(u'This action is disabled', 'error')
                elif action_name == 'delete_selected':
                    if self.can_delete:
                        try:
                            ids = self.get_selected_ids()
                            if ids:
                                self.do_delete_selected(ids)
                            else:
                                flask(u'Invalid selection', 'error')
                        except Exception as e:
                            flash(u'ERROR: %s' % str(e), 'error')
                    else:
                        flash(u'This action is disabled', 'error')

        # listamos os registros
        page = request.args.get('page', 1, type=int)
        objects = Pagination(self.get_objects(), page, self.per_page)
        context = {
            # actions:
            'can_create': self.can_create,
            'can_update': self.can_update,
            'can_delete': self.can_delete,
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
