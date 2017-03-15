# coding: utf-8
import os
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, render_template, request, flash, redirect, url_for
from opac_proc.web.webapp import login_manager
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

import forms
from mixins import User
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
                    if login_user(user, remember="no"):
                        flash("Logged in!")
                        return redirect(next_url)
                    else:
                        flash("unable to log you in")
                except:
                    flash("unable to register with that email address")
            else:
                flash("Fix form errors")

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
    flash("Logged out.")
    return redirect(url_for('accounts.login'))
