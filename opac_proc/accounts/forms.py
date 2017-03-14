# coding: utf-8
import models
from flask_mongoengine.wtf import model_form
from flask_mongoengine.wtf.orm import validators
from wtforms.fields import PasswordField, BooleanField

user_form = model_form(models.User, exclude=['password', 'active', 'timestamp'])


# Signup Form created from user_form
class RegisterForm(user_form):
    password = PasswordField(
        'password',
        validators=[
            validators.Required(),
            validators.EqualTo('confirm', message='Passwords must match')
        ])
    confirm = PasswordField('repeat password')


# Login form will provide a Password field (WTForm form field)
class LoginForm(user_form):
    password = PasswordField(
        'password',
        validators=[validators.Required()])
    remember = BooleanField(
        'remember')
