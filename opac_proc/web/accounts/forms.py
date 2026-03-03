# coding: utf-8
from . import models
from flask_wtf import FlaskForm
from flask_mongoengine.wtf import model_form
from flask_mongoengine.wtf.orm import validators
from wtforms.fields import PasswordField, BooleanField, EmailField


UserForm = model_form(models.User, exclude=[
    'password',
    'active',
    'timestamp',
    'email_confirmed'
])


# Signup Form created from UserForm
class RegisterForm(UserForm):
    password = PasswordField(
        'password',
        validators=[
            validators.DataRequired(),
            validators.EqualTo('confirm', message='Passwords must match')
        ])
    confirm = PasswordField('repeat password')


# Login form will provide a Password field (WTForm form field)
class LoginForm(UserForm):
    password = PasswordField(
        'password',
        validators=[validators.DataRequired()])
    remember = BooleanField(
        'remember')


class EmailForm(FlaskForm):
    email = EmailField(
        'email',
        validators=[
            validators.DataRequired(),
            validators.Email()
        ])


class PasswordForm(FlaskForm):
    password = PasswordField(
        'password',
        validators=[validators.DataRequired()])
