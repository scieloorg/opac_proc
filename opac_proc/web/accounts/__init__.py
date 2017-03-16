# coding: utf-8
from flask import Blueprint

accounts = Blueprint(
    'accounts', __name__,
    template_folder='templates',
    static_folder='static')

from . import views  # NOQA
