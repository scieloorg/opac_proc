# coding: utf-8
from flask import current_app
from opac_proc.datastore.models import Message
from opac_proc.web.accounts.models import User


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
    from flask_mail import Message as FlaskMailMessage
    recipients = [recipient, ]
    if isinstance(recipient, list):
        recipients = recipient
    try:
        subject = "[%s] %s" % (current_app.config['OPAC_PROC_COLLECTION'], subject)
        msg = FlaskMailMessage(
            subject=subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=recipients,
            html=html)
        mail.send(msg)
        return (True, '')
    except Exception as e:
        return (False, e.message)


class AppMessage(object):
    model_instance = None

    def __init__(self, subject, body, stage='default', model_name='', unread=True, msg_type='DEFAULT'):
        msg_data = {
            'subject': subject,
            'body': body,
            'stage': stage,
            'model_name': model_name,
            'unread': unread,
            'msg_type': msg_type,
        }
        self.model_instance = Message(**msg_data)

    @property
    def pk(self):
        if self.model_instance is None:
            raise AttributeError(u'O attr: model_instance não foi definido!')
        else:
            return self.model_instance.pk

    def save(self):
        if self.model_instance is None:
            raise AttributeError(u'O attr: model_instance não foi definido!')
        else:
            self.model_instance.save()

    def send_email(self):
        if self.model_instance is None or not self.model_instance.pk:
            raise ValueError(u'Antes de enviar email deve salvar a mensagem! Utilize o método save()')
        else:
            users = User.objects.filter(active=True, email_confirmed=True)
            for user in users:
                send_email(
                    recipient=user.email,
                    subject=self.model_instance.subject,
                    html=self.model_instance.body)


def create_default_msg(subject, body, stage='default', model_name='', unread=True):
    msg = AppMessage(subject, body, stage, model_name, unread, 'DEFAULT')
    msg.save()
    return msg


def create_error_msg(subject, body, stage='default', model_name='', unread=True):
    msg = AppMessage(subject, body, stage, model_name, unread, 'ERROR')
    msg.save()
    return msg


def create_warning_msg(subject, body, stage='default', model_name='', unread=True):
    msg = AppMessage(subject, body, stage, model_name, unread, 'WARNING')
    msg.save()
    return msg


def create_info_msg(subject, body, stage='default', model_name='', unread=True):
    msg = AppMessage(subject, body, stage, model_name, unread, 'INFO')
    msg.save()
    return msg


def create_debug_msg(subject, body, stage='default', model_name='', unread=True):
    msg = AppMessage(subject, body, stage, model_name, unread, 'DEBUG')
    msg.save()
    return msg


def send_email_unread_single_message(msg_id):
    try:
        msg = Message.object.get(pk=msg_id)
        if msg.model_instance.unread:
            msg.send_email()
        else:
            raise ValueError(u'A mensagem com id: %s já esta marcada como enviada e não sera enviada novamente!' % msg_id)
    except Message.DoesNotExists:
        raise ValueError(u'A mensagem com id: %s não existe!' % msg_id)
    except Exception, e:  # melhorar esta Exception com IOError ou socket.error
        raise Exception(u'A mensagem com id: %s não pode ser enviada! Erro: %s' % (msg_id, str(e)))


def send_email_unread_mass_messages(msg_ids):
    msgs = Message.object.filter(pk__in=msg_ids)
    for msg in msgs:
        send_email_unread_single_message(msg.pk)
