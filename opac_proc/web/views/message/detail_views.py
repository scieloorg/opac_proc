# coding: utf-8
from flask import request, abort, url_for, jsonify, flash
from opac_proc.datastore import models
from opac_proc.web.views.generics.detail_views import DetailView


class MessageDetailView(DetailView):
    methods = ['GET', 'PUT', 'DELETE']
    model_class = models.Message
    page_title = u'Message Detail'
    template_name = 'message/detail.html'

    def get_document_by_id(self, object_id):
        """
        metodo que retorna o documento procurando pelo object_id.
        """
        return self.model_class.objects.get(id=object_id)

    def put(self, object_id):
        expected_actions = [
            'mark_as_unread',
            'mark_as_read',
        ]

        if 'action' not in request.form.keys():
            abort(400, u'Não foi enviado o param. "action" na requisição!')
        elif request.form['action'] not in expected_actions:
            abort(400, u'Não param. "action" enviado na requisição não é válido!')
        else:
            action = request.form['action']
            try:
                obj = self.get_document_by_id(object_id)
                if action == 'mark_as_unread' or action == 'mark_as_read':
                    if action == 'mark_as_unread':
                        obj.unread = True
                        flash('Mensagem marcada como NÃO LIDA, com sucesso!', 'success')
                    else:
                        obj.unread = False
                        flash('Mensagem marcada como LIDA, com sucesso!', 'success')
                    obj.save()
                return jsonify({
                    'updated': True,
                    'location': url_for('default.message_detail', object_id=object_id)
                })
            except models.Message.DoesNotExist:
                abort(404, u'Mensagem não existe (id: %s)' % object_id)

    def delete(self, object_id):
        try:
            obj = self.get_document_by_id(object_id)
            obj.delete()
            return jsonify({
                'deleted': True,
                'location': url_for('default.message_list')
            })
        except models.Message.DoesNotExist:
            abort(404, u'Mensagem (com id: %s) não existe' % object_id)
