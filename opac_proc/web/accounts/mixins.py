# coding: utf-8

import logging

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    current_user, login_required, logout_user,
    UserMixin, AnonymousUserMixin,
    confirm_login, fresh_login_required)
import models
import notifications

logger = logging.getLogger(__name__)


class User(UserMixin):
    def __init__(self, email=None, password=None, active=True, id=None, email_confirmed=False):
        self.email = email
        self.password = password
        self.active = active
        self.email_confirmed = email_confirmed
        self.id = None

    def save(self):
        new_user = models.User(
            email=self.email,
            password=self.password,
            active=self.active,
            email_confirmed=self.email_confirmed)
        new_user.save()
        self.id = new_user.id
        return self.id

    def get_by_email(self, email):
        try:
            db_user = models.User.objects.get(email=email)
        except models.User.DoesNotExist as e:
            logger.warning(str(e))
            return None
        else:
            self.email = db_user.email
            self.active = db_user.active
            self.id = db_user.id
            self.email_confirmed = db_user.email_confirmed
            return self

    def get_by_email_w_password(self, email):
        try:
            db_user = models.User.objects.get(email=email)

            if db_user:
                self.email = db_user.email
                self.active = db_user.active
                self.password = db_user.password
                self.id = db_user.id
                self.email_confirmed = db_user.email_confirmed
                return self
            else:
                logger.error(u"Can not retrieve user by email from email: %s", email)
                return None
        except models.User.DoesNotExist as e:
            logger.warning(str(e))
            return None

    def get_user_db_instance(self):
        if self.id:
            try:
                return models.User.objects.with_id(self.id)
            except models.User.DoesNotExist:
                raise ValueError('User does not exists with this id: %s' % self.id)
        else:
            raise ValueError('Invalid id to retrieve user instance. id: %s' % self.id)

    def get_by_id(self, id):
        try:
            db_user = models.User.objects.with_id(id)
        except models.User.DoesNotExist:
            raise ValueError('User does not exists with this id: %s' % self.id)
        else:
            if db_user:
                self.email = db_user.email
                self.active = db_user.active
                self.id = db_user.id
                self.email_confirmed = db_user.email_confirmed
                return self
            else:
                return None

    def set_email_confirmed(self):
        db_user = self.get_user_db_instance()
        db_user.email_confirmed = True
        db_user.save()
        db_user.reload()

    def send_confirmation_email(self):
        """
        Envia um email de confirmação para ``db_user.email``
        Retorna:
         - (True, '') em caso de sucesso.
         - (False, 'MENSAGEM DE ERRO/EXCEÇÃO') em caso de exceção/erro
        """
        db_user = self.get_user_db_instance()
        return notifications.send_confirmation_email(db_user.email)

    def send_reset_password_email(self):
        db_user = self.get_user_db_instance()
        return notifications.send_reset_password_email(self.email)

    def set_new_password(self, password_as_plain_text):
        db_user = self.get_user_db_instance()
        # generate password hash
        password_hash = generate_password_hash(password_as_plain_text)
        db_user.password = password_hash
        db_user.save()
        db_user.reload()

    @staticmethod
    def generate_password_hash(password_as_plain_text):
        """
        Return a password hash from a password_as_plain_text string
        """
        return generate_password_hash(password_as_plain_text)

    def check_password_hash(self, password_as_plain_text):
        """
        Return True or False if password_as_plain_text match with self.password
        """
        return check_password_hash(self.password, password_as_plain_text)


class Anonymous(AnonymousUserMixin):
    name = u"Anonymous"
