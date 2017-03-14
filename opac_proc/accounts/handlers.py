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


def check_user_logged_in_or_redirect():
    """
    Verifica se o usuário retornado pelo flask_admin.current_user esta logado.
    Se não estiver, redireciona para página de login,
    notificando ao cliente com um flash.
    """

    if not current_user.is_authenticated:
        flash(u'Please log in to access this page.')
        return redirect(url_for('accounts.login', next=request.path or '/'))
