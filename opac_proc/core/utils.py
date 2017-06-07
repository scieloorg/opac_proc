# coding: utf-8

from jinja2 import FileSystemLoader, Environment


class Singleton(object):
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instances[cls]


def render_from_template(directory, template_name, kwargs):

    loader = FileSystemLoader(directory)
    env = Environment(loader=loader)
    template = env.get_template(template_name)

    return template.render(**kwargs)
