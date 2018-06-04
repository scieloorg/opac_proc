from flask import Response
from prometheus_client import generate_latest


CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')


def prometheus_metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
