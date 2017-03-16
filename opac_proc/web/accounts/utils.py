# coding: utf-8
import re
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from flask import current_app, url_for


REGEX_EMAIL = re.compile(
    r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?",
    re.IGNORECASE)  # RFC 2822 (simplified)


def get_timed_serializer():
    """
    Retorna uma instância do URLSafeTimedSerializer necessário para gerar tokens
    """
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def send_email(recipient, subject, html):
    """
    Método auxiliar para envio de emails
    - recipient: email do destinatario, ou lista de emails dos destinatarios
    - subject: assunto
    - html: corpo da mensagem (formato html)
    Quem envía a mensagem é que for definido na configuração: 'MAIL_DEFAULT_SENDER'

    Retorna:
     - (True, '') em caso de sucesso.
     - (False, 'MENSAGEM DE ERRO/EXCEÇÃO') em caso de exceção/erro
    """
    from opac_proc.web.webapp import mail
    recipients = [recipient, ]
    if isinstance(recipient, list):
        recipients = recipient
    try:
        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=recipients,
            html=html)
        mail.send(msg)
        return (True, '')
    except Exception as e:
        return (False, e.message)
