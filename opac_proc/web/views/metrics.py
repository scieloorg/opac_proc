# coding: utf-8
from flask import Response, current_app, abort
from prometheus_client import generate_latest


CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')


def prometheus_metrics():
    """
    Se a conf tiver ativado: PROMETHEUS_ENABLED
    Retorna a resposta com as metricas para prometheus
    Caso contrario retorna 404
    """

    is_enable = current_app.config['PROMETHEUS_ENABLED']
    if is_enable:
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
    else:
        abort(404, u'As metricas de prometheus estão desativadas')
