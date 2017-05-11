# coding: utf-8
import json
from flask import render_template, abort
from flask.views import MethodView
from mongoengine import DoesNotExist, MultipleObjectsReturned


class DetailView(MethodView):
    model_class = None
    template_name = 'object_detail/base.html'
    page_title = u'Object Detail'
    page_subtitle = u''

    def get_document_by_id(self, object_id):
        """
        metodo que retorna o documento procurando pelo object_id.
        """
        return self.model_class.objects.get(_id=object_id)

    def render_template(self, context):
        return render_template(self.template_name, **context)

    def get(self, object_id):
        model_class_name = str(self.model_class)
        if object_id is None:
            abort(400, u'Deve indicar um id (parametro: object_id) válido')
        else:
            try:
                doc = self.get_document_by_id(object_id)
                doc_json = doc.to_json()
                doc_json = json.loads(doc_json)
            except DoesNotExist:
                abort(404, u'Recurso não existe (%s, %s)' % (
                      model_class_name, object_id))
            except MultipleObjectsReturned:
                abort(404, u'Existe mais de um recurso com esse id: (%s, %s)' % (
                      model_class_name, object_id))
            except Exception, e:
                abort(500, u'Exception: %s (%s, %s)' % (
                      e, model_class_name, object_id))
            else:
                context = {
                    'page_title': self.page_title,
                    'page_subtitle': u'(%s)' % object_id,
                    'object_json': doc_json,
                    'document': doc
                }
                return self.render_template(context)
