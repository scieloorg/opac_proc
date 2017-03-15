# coding: utf-8
import os
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import abort, current_app, render_template, request, flash, redirect, url_for
from opac_proc.web.webapp import login_manager
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

import forms
from mixins import User
from utils import get_timed_serializer
from . import accounts


@accounts.route("/accounts/login", methods=["GET", "POST"])
def login():
    form = forms.LoginForm(request.form)
    if request.method == "POST":
        if form.validate():
            email = form.data["email"]
            password_as_plain_text = form.data["password"]
            remember = form.data.get("remember", False)
            next_url = form.data.get("next", request.args.get("next", "/"))
            user_obj = User()
            user = user_obj.get_by_email_w_password(email)
            if user is None:
                flash(u"User with this email Does Not Exists", "error")
            elif not user.is_active:
                flash(u"This user is inactive", "warning")
            elif if current_app.config['ACCOUNTS_REQUIRES_EMAIL_CONFIRMATION'] and not user.email_confirmed:
                flash(u"This user has unconfirmed email", "warning")
            else:
                password_is_valid = check_password_hash(user.password, password_as_plain_text)
                if password_is_valid:
                    if login_user(user, remember=remember):
                        flash(u"Logged in!", "success")
                        return redirect(next_url)
                    else:
                        flash(u"unable to log you in", "error")
                else:
                    flash(u"Wrong password", "error")
        else:
            flash(u"Fix form errors", "error")

    context = {
        'form': form
    }
    return render_template("accounts/login.html", **context)


@accounts.route("/accounts/register/disabled")
def register_disabled():
    return render_template("accounts/registration_disabled.html")


@accounts.route("/accounts/register", methods=["GET", "POST"])
def register():

    if current_app.config['WEB_REGISTRATION_ENABLED']:
        form = forms.RegisterForm(request.form)

        if request.method == 'POST':
            if form.validate():
                email = request.form['email']
                password_as_plain_text = request.form['password']
                next_url = request.form.get("next", request.args.get("next", "/"))
                # generate password hash
                password_hash = generate_password_hash(password_as_plain_text)
                # prepare User
                user = User(email, password_hash)
                try:
                    user.save()
                    if current_app.config['ACCOUNTS_REQUIRES_EMAIL_CONFIRMATION']:
                        msg_sent, msg_error = user.send_confirmation_email()
                        if msg_sent:
                            flash(u"Email sent with a link for confirmation (%s)!" % email, "success")
                        else:
                            flash(u"Can't sent the email (to: %s) with confirmation link! Error: %s" % (email, msg_error), "error")
                    else:
                        # se não é requerido, já deixamos o email como confirmado
                        user.set_email_confirmed()

                    if user.email_confirmed:
                        if login_user(user, remember="no"):
                            flash(u"Logged in!", "success")
                            return redirect(next_url)
                        else:
                            flash(u"Unable to log you in", "error")
                    else:
                        return render_template("accounts/unconfirm_email.html")
                except Exception as e:
                    flash(u"Unable to register with that email address: %s. Error: %s" % (email, unicode(e)), "error")
            else:
                flash(u"Fix form errors", "error")

        context = {
            'form': form
        }
        return render_template("accounts/register.html", **context)
    else:
        return redirect(url_for('accounts.register_disabled'))


@accounts.route("/accounts/logout")
@login_required
def logout():
    logout_user()
    flash(u"Logged out.")
    return redirect(url_for('accounts.login'))


@accounts.route("/accounts/reset/password/<token>", methods=["GET", "POST"])
def reset_password_with_token(token):
    try:
        ts = get_timed_serializer()
        email = ts.loads(
            token,
            salt="recover-key",
            max_age=current_app.config['TOKEN_MAX_AGE'])
    except Exception:
        abort(404)

    form = forms.PasswordForm(request.form)
    if admin.helpers.validate_form_on_submit(form):
        user = controllers.get_user_by_email(email=email)
        if not user.email_confirmed:
            return render_template("accounts/unconfirm_email.html")

        controllers.set_user_password(user, form.password.data)
        flash(u"New password saved successfully!", "success")
        return redirect(url_for('accounts.login'))
    context = {
        'form': form,
        'token': token,
    }
    return render_template('accounts/reset_with_token.html', **context)


@accounts.route("/accounts/reset/password", methods=["GET", "POST"])
def reset_password():
    form = forms.EmailForm(request.form)

    if request.method == 'POST':
        if form.validate():
            email = request.form['email']
            user_obj = User()
            user = user_obj.get_by_email(email)

            if not user:
                abort(404, "User not found")

            if not user.email_confirmed:
                return render_template("accounts/unconfirm_email.html")

            msg_sent, error_msg = user.send_reset_password_email()
            if msg_sent:
                msg = u"Enviamos as instruções para recuperar a senha para: %s" % user.email
                flash(msg, 'success')
            else:
                msg = u"Ocorreu um erro no envio das instruções por email para: %s. Erro: %s" % (
                    user.email, error_msg)
                flash(msg, 'error'),
            return redirect(url_for('accounts.login'))
        else:
            flash(u"Fix form errors", "error")

    context = {
        'form': form
    }
    return render_template("accounts/reset_password.html", **context)


@accounts.route("/accounts/confirm/<token>", methods=["GET", ])
def confirm_email(token):
    try:
        ts = get_timed_serializer()
        email = ts.loads(
            token,
            salt="email-confirm-key",
            max_age=current_app.config['TOKEN_MAX_AGE'])
    except Exception:  # possiveis exceções: https://pythonhosted.org/itsdangerous/#exceptions
        # qualquer exeção invalida a operação de confirmação
        abort(404)  # melhorar mensagem de erro para o usuário

    user = User().get_by_email(email)
    if user:
        user.set_email_confirmed()
        flash(u'Email: %s confirmed successfully! Now you can login!' % user.email, 'success')
        return redirect(url_for('accounts.login'))
    else:
        abort(404, u"User not found")
