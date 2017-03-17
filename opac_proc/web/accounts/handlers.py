# coding: utf-8

from flask import request, flash, redirect, url_for
from flask_login import current_user
from opac_proc.web.webapp import login_manager
from .mixins import User


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('accounts.login'))


@login_manager.user_loader
def load_user(id):
    if id is None:
        redirect(url_for('accounts.login'))
    user = User()
    user.get_by_id(id)
    if user.is_active:
        return user
    else:
        return None
