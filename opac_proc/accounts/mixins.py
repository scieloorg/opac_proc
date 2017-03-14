# coding: utf-8
import os

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager, current_user, login_required,
    login_user, logout_user, UserMixin, AnonymousUserMixin,
    confirm_login, fresh_login_required)
import models


class User(UserMixin):
    def __init__(self, email=None, password=None, active=True, id=None):
        self.email = email
        self.password = password
        self.active = active
        self.id = None

    def save(self):
        new_user = models.User(email=self.email, password=self.password, active=self.active)
        new_user.save()
        self.id = new_user.id
        return self.id

    def get_by_email(self, email):
        db_user = models.User.objects.get(email=email)
        if db_user:
            self.email = db_user.email
            self.active = db_user.active
            self.id = db_user.id
            return self
        else:
            return None

    def get_by_email_w_password(self, email):
        try:
            db_user = models.User.objects.get(email=email)

            if db_user:
                self.email = db_user.email
                self.active = db_user.active
                self.password = db_user.password
                self.id = db_user.id
                return self
            else:
                # logger
                return None
        except models.User.DoesNotExist as e:
            # logger
            return None

    def get_user_db_instance(self):
        if self.id:
            return models.User.objects.with_id(self.id)
        else:
            return None

    def get_by_id(self, id):
        db_user = models.User.objects.with_id(id)
        if db_user:
            self.email = db_user.email
            self.active = db_user.active
            self.id = db_user.id
            return self
        else:
            return None


class Anonymous(AnonymousUserMixin):
    name = u"Anonymous"
