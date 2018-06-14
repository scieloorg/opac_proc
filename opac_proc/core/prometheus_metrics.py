# coding: utf-8
from functools import wraps
from urllib2 import URLError

from prometheus_client import (
    Summary, CollectorRegistry, pushadd_to_gateway,
    instance_ip_grouping_key)

from opac_proc.web import config

metrics = {
    'ex_articles_extract_method_processing_seconds': {
        'type': 'summary',
        'help': 'Time spent processing during execution of extract method (ex_articles)'
    },
    'amapi_thirft_get_article_request_processing_seconds': {
        'type': 'summary',
        'help': 'AM API THRIFT Time spent processing request'
    }
}


def get_job_name_of_func(func):
    func_module = func.__module__
    func_name = func.__name__
    return "%s.%s" % (func_module, func_name)


def get_metric_instance_by_name(metric_name, custom_registry=None):
    if metric_name not in metrics.keys():
        raise ValueError(u'Não foi encontrada uma metrica com esse nome. foi definida?')
    else:
        metric_definition = metrics[metric_name]
        if metric_definition['type'] == 'summary':
            if custom_registry is None:
                return Summary(
                    metric_name,
                    metric_definition['help']
                )
            else:
                return Summary(
                    metric_name,
                    metric_definition['help'],
                    registry=custom_registry
                )
        else:
            raise ValueError('O valor de "type" da metrica com nome: %s não é válido!' % metric_name)


def push_metric(metric_name):
    registry_instance = CollectorRegistry()
    metric = get_metric_instance_by_name(metric_name, registry_instance)

    def real_decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if config.PROMETHEUS_ENABLED:

                with metric.time():
                    result = function(*args, **kwargs)

                try:
                    pushadd_to_gateway(
                        config.PROMPG_URL,
                        job=get_job_name_of_func(function),
                        grouping_key=instance_ip_grouping_key(),
                        registry=registry_instance)
                except URLError:
                    pass  # ignoramos erros de conexão enviado as metricas
            else:
                result = function(*args, **kwargs)

            return result
        return wrapper
    return real_decorator
