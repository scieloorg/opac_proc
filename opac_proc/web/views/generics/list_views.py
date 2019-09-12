# coding: utf-8
import re
import traceback
from datetime import datetime, timedelta
from flask import render_template, flash, request, url_for
from flask.views import View
from flask_mongoengine import Pagination
from flask_login import current_user

from opac_proc.core.notifications import (
    # create_default_msg,
    create_error_msg,
    # create_warning_msg,
    create_info_msg,
    # create_debug_msg,
)


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
    list_columns = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'string'
        },
        {
            'field_label': u'Last update',
            'field_name': 'metadata.updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Process completed?',
            'field_name': 'metadata.process_completed',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Must reprocess?',
            'field_name': 'metadata.must_reprocess',
            'field_type': 'boolean'
        },
    ]

    can_process = False
    can_delete = False

    list_filters = [
        {
            'field_label': u'UUID',
            'field_name': 'uuid',
            'field_type': 'uuid'
        },
        {
            'field_label': u'Last update',
            'field_name': 'metadata.updated_at',
            'field_type': 'date_time'
        },
        {
            'field_label': u'Process completed?',
            'field_name': 'metadata.process_completed',
            'field_type': 'boolean'
        },
        {
            'field_label': u'Must reprocess?',
            'field_name': 'metadata.must_reprocess',
            'field_type': 'boolean'
        },
    ]

    _allowed_POST_action_names = [
        'process_all',
        'process_selected',
        'delete_all',
        'delete_selected'
    ]

    filter_string_options = (
        ('iexact', 'Exact'),
        ('icontains', 'Contains'),
        ('istartswith', 'Starts with'),
        ('iendswith', 'Ends with')
    )

    custom_actions = [
        # {
        #     'method_name': 'do_foo_bar',    # nome de função python que implementa a ação
        #     'label': 'Foo Bar',             # nome da ação para mostrar pro usuário
        #     'icon_class': 'fa fa-user',     # class CSS para o icone. ex: 'fa fa-gear'
        #     'can_select_rows': True,        # boolean, se permite ou não a opção "All/Selected" ou não
        # },
    ]
    convert_pk_to_uuid = False

    def _valid_uuid(self, uuid):
        regex = re.compile(r'^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
        match = regex.match(uuid)
        return bool(match)

    def get_filters(self):
        qs_filters = {}
        filter_string_lookups = dict(self.filter_string_options).keys()

        if request.method == 'GET':
            for list_filter in self.list_filters:

                f_field_name = list_filter['field_name']
                f_field_type = list_filter['field_type']
                f_field_label = list_filter['field_label']

                qs_filter_value = request.args.get('filter__value__%s' % f_field_name, None)
                qs_filter_from = request.args.get('filter__value__from__%s' % f_field_name, None)
                qs_filter_until = request.args.get('filter__value__until__%s' % f_field_name, None)
                qs_filter_option = request.args.get('filter__option__%s' % f_field_name, None)

                if f_field_type == 'string' and qs_filter_value:
                    qs_filter_value = qs_filter_value.strip()

                    if qs_filter_value and qs_filter_option and qs_filter_option in filter_string_lookups:
                        field_lookup = f_field_name + '__' + qs_filter_option
                        qs_filters[field_lookup] = qs_filter_value
                    else:
                        flash('filter for: "%s" is invalid' % f_field_label, 'warning')
                        continue  # ignore this filter

                elif f_field_type == 'uuid' and qs_filter_value:

                    qs_filter_value = qs_filter_value.strip()
                    if self._valid_uuid(qs_filter_value):
                        qs_filters[f_field_name] = str(qs_filter_value)
                    else:
                        flash('Filter for: "%s". It is not a valid UUID value' % f_field_label, 'error')
                        continue  # ignore this filter

                elif f_field_type == 'boolean' and qs_filter_value:
                    qs_filter_value = qs_filter_value.strip()

                    if qs_filter_value == "true":
                        qs_filters[f_field_name] = True
                    elif qs_filter_value == "false":
                        qs_filters[f_field_name] = False
                    # else:  ignore

                elif f_field_type == 'date_time':

                    if qs_filter_from and qs_filter_until:
                        # convert datetime string to datetime objects
                        qs_filter_from = datetime.strptime(qs_filter_from, "%Y-%m-%d %H:%M:%S")
                        qs_filter_until = datetime.strptime(qs_filter_until, "%Y-%m-%d %H:%M:%S")
                        qs_filter_until_plus_1 = qs_filter_until + timedelta(seconds=1)
                        qs_filters['__raw__'] = {
                            f_field_name: {
                                '$gte': qs_filter_from,
                                '$lte': qs_filter_until_plus_1,
                            }
                        }
                    elif qs_filter_from:  # falta: qs_filter_until
                        flash('Filter for: "%s" was ignored. You must fill the "Until:" date time field!' % f_field_label, 'warning')
                        continue
                    elif qs_filter_until:  # falta: qs_filter_from
                        flash('Filter for: "%s" was ignored. You must fill the "From:" date time field!' % f_field_label, 'warning')
                        continue
                    else:
                        continue  # date time filter not filled. Ignoring

                elif f_field_type == 'choices' and qs_filter_option:

                    filter_choices = [opt[0] for opt in list_filter['field_options']]
                    if qs_filter_option and qs_filter_option in filter_choices:
                        qs_filters[f_field_name] = qs_filter_option
                    else:
                        flash('filter for: "%s" is invalid' % f_field_label, 'warning')
                        continue  # ignore this filter

            return qs_filters
        else:
            return qs_filters

    def get_objects(self):
        if self.model_class is None:
            raise ValueError("model class not defined")
        else:
            filters = self.get_filters()
            if self.list_filters and filters:
                _filters = {
                    field.replace('.', '__'): value
                    for field, value in filters.items()
                }
                return self.model_class.objects.filter(**_filters)
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

    def _trigger_messages(self, is_error=False, exception_obj=None, traceback_str='', items_count=None):
        user = current_user.email
        if is_error:
            exception_msg = u"{exception_str} {traceback_str}".format(
                            exception_str=unicode(exception_obj),
                            traceback_str=traceback_str)

            msg_subject = u"ERRO: Após o usuário: {user} iniciar o processo de: {stage} para o modelo: {model} via web".format(
                user=user, stage=self.stage, model=self.model_name)

            qty = items_count or 'todos os'
            msg_body = u"""
                        <strong>ERRO:</strong><br />
                        Ocorreu um erro após o usuário: <strong>{user}</strong> iniciar o processo de: <strong>{stage}</strong>
                        para {qty} registro(s) de: <strong>{model}</strong> via web <br /><br />
                        {exception_msg}
                        """.format(user=user, stage=self.stage, model=self.model_name, exception_msg=exception_msg, qty=qty)
            app_msg = create_error_msg(msg_subject, msg_body, self.stage, self.model_name)
            msg_link = url_for('default.message_detail', object_id=app_msg.pk, _external=True)
            flask_msg = u'{msg}. Descrição completa do erro <a href="{url}">aqui</a>'.format(msg=msg_subject, url=msg_link)
            flash(flask_msg, 'error')
            app_msg.send_email()
        else:
            msg_subject = u"Usuário: {user} iniciou o processo de: {stage} para o modelo: {model} via web".format(
                          user=user, stage=self.stage,
                          model=self.model_name)
            qty = items_count or 'todos os'
            msg_body = u"""
                        Usuário: <strong>{user}</strong> iniciar o processo de: <strong>{stage}</strong>
                        para {qty} registros de <strong>{model}</strong>, via web.
                        """.format(user=user, stage=self.stage, model=self.model_name, qty=qty)
            app_msg = create_info_msg(msg_subject, msg_body, self.stage, self.model_name)
            msg_link = url_for('default.message_detail', object_id=app_msg.pk, _external=True)
            flask_msg = u'{msg}. Descrição completa <a href="{url}">aqui</a>'.format(msg=msg_subject, url=msg_link)
            flash(flask_msg, 'info')
            app_msg.send_email()

    def do_process_all(self):
        try:
            processor = self.process_class()
            processor.all()
        except Exception, e:
            traceback_str = traceback.format_exc()
            self._trigger_messages(is_error=True, exception_obj=e, traceback_str=traceback_str)
        else:
            self._trigger_messages()

    def do_process_selected(self, selected_uuids):
        try:
            processor = self.process_class()
            processor.selected(selected_uuids)
        except Exception as e:
            traceback_str = traceback.format_exc()
            self._trigger_messages(is_error=True, exception_obj=e, traceback_str=traceback_str, items_count=len(selected_uuids))
        else:
            self._trigger_messages(items_count=len(selected_uuids))

    def do_delete_all(self):
        try:
            processor = self.process_class()
            processor.delete_all()
        except Exception as e:
            traceback_str = traceback.format_exc()
            self._trigger_messages(is_error=True, exception_obj=e, traceback_str=traceback_str)
        else:
            self._trigger_messages()

    def do_delete_selected(self, selected_uuids):
        try:
            processor = self.process_class()
            processor.delete_selected(selected_uuids)
        except Exception as e:
            traceback_str = traceback.format_exc()
            self._trigger_messages(is_error=True, exception_obj=e, traceback_str=traceback_str, items_count=len(selected_uuids))
        else:
            self._trigger_messages(items_count=len(selected_uuids))

    def get_selected_ids(self, return_as_uuid_str=False):
        pks = request.form.getlist('rowid')
        if not pks:
            raise ValueError(u"Não selecionou registros!")
        elif isinstance(pks, list):
            pks = [_id.strip() for _id in pks]
            if return_as_uuid_str:
                selected_uuids = self.model_class.objects.filter(pk__in=pks).values_list('uuid')
                return [str(uuid) for uuid in selected_uuids]
        else:
            raise ValueError("Seleção inválida: %s" % pks)
        return pks

    def dispatch_request(self):
        if request.method == 'POST':  # create action
            action_name = request.form['action_name']
            if action_name.startswith('custom_action__'):
                _, custom_action_method_name, custom_action_target = action_name.split('__')
                custom_methods_defined = [c_actions['method_name'] for c_actions in self.custom_actions]
                if custom_action_method_name not in custom_methods_defined:
                    flash(u'Ação inválida: %s. Nenhum registro foi alterado.' % custom_action_method_name, 'error')
                elif not hasattr(self, custom_action_method_name):
                    flash(u'O método: %s não foi implementado, na ListView. Nenhum registro foi alterado.' % custom_action_method_name, 'error')
                else:
                    if custom_action_target == 'selected':
                        try:
                            ids = self.get_selected_ids()
                            if ids:
                                concrete_method = getattr(self, custom_action_method_name)
                                concrete_method(ids)
                            else:
                                flash(u'Seleção inválida de registros. Nenhum registro foi alterado.', 'error')
                        except Exception as e:
                            flash(u'ERRO: %s' % str(e), 'error')
                    else:
                        try:
                            concrete_method = getattr(self, custom_action_method_name)
                            concrete_method()
                        except Exception as e:
                            flash(u'ERRO: %s' % str(e), 'error')

            elif action_name in self._allowed_POST_action_names:
                if action_name == 'process_all':
                    if self.can_process:
                        try:
                            self.do_process_all()
                        except Exception as e:
                            flash(u'ERRO: %s' % str(e), 'error')
                    else:
                        flash(u'Esta ação não esta habilitada. Nenhum registro foi alterado.', 'error')
                elif action_name == 'process_selected':
                    if self.can_process:
                        try:
                            ids = self.get_selected_ids(self.convert_pk_to_uuid)
                            if ids:
                                self.do_process_selected(ids)
                            else:
                                flash(u'Seleção inválida de registros. Nenhum registro foi alterado.', 'error')
                        except Exception as e:
                            flash(u'ERRO: %s' % str(e), 'error')
                    else:
                        flash(u'Esta ação não esta habilitada. Nenhum registro foi alterado.', 'error')
                elif action_name == 'delete_all':
                    if self.can_delete:
                        try:
                            self.do_delete_all()
                        except Exception as e:
                            flash(u'ERRO: %s' % str(e), 'error')
                    else:
                        flash(u'Esta ação não esta habilitada. Nenhum registro foi alterado.', 'error')
                elif action_name == 'delete_selected':
                    if self.can_delete:
                        try:
                            ids = self.get_selected_ids(self.convert_pk_to_uuid)
                            if ids:
                                self.do_delete_selected(ids)
                            else:
                                flash(u'Seleção inválida de registros', 'error')
                        except Exception as e:
                            flash(u'ERRO: %s' % str(e), 'error')
                    else:
                        flash(u'Esta ação não esta habilitada. Nenhum registro foi alterado.', 'error')
            else:
                flash(u'Ação inválida: %s. Nenhum registro foi alterado.' % action_name)
        # listamos os registros
        page = request.args.get('page', 1, type=int)

        new_per_page = request.args.get('per_page', self.per_page, type=int)
        if self.per_page != new_per_page:
            if new_per_page in [10, 20, 50, 100, 500, 1000]:
                self.per_page = new_per_page

        objects = Pagination(self.get_objects(), page, self.per_page)
        context = {
            # stage: 'extract' || 'transform' || 'load' || 'opac'
            'stage': self.stage,
            # filters:
            'list_filters': self.list_filters,
            'filter_string_options': self.filter_string_options,
            # actions:
            'can_process': self.can_process,
            'can_delete': self.can_delete,
            # meta:
            'page_title': self.page_title,
            'page_subtitle': self.page_subtitle,
            'panel_title': self.panel_title,
            'list_columns': self.list_columns,
            # objetos:
            'objects': objects.items,
            # paginas:
            'pager_range': self._pager_range(page, objects.pages),
            'current_page': page,
            'per_page': self.per_page,
            'total_pages': objects.pages,
            'total_records': objects.total,
            'has_prev': objects.has_prev,
            'prev_num': objects.prev_num,
            'has_next': objects.has_next,
            'next_num': objects.next_num,
            # custom actions:
            'custom_actions': self.custom_actions
        }
        return self.render_template(context)
