# coding: utf-8

from flask import request, flash, redirect, url_for
from flask_login import current_user


def check_user_logged_in_or_redirect():
    """
    Verifica se o usuário retornado pelo flask_admin.current_user esta logado.
    Se não estiver, redireciona para página de login,
    notificando ao cliente com um flash.
    """

    if not current_user.is_authenticated:
        flash(u'Please log in to access this page.')
        return redirect(url_for('accounts.login', next=request.path or '/'))
