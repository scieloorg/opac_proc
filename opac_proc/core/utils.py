
from jinja2 import FileSystemLoader, Environment


def render_from_template(directory, template_name, kwargs):

    loader = FileSystemLoader(directory)
    env = Environment(loader=loader)
    template = env.get_template(template_name)

    return template.render(**kwargs)
