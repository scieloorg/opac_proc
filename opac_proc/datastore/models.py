# coding: utf-8
from datetime import datetime
from mongoengine import (
    Document,
    DynamicDocument,
    signals,
    StringField,
    DateTimeField,
    BooleanField
)
from base_mixin import BaseMixin

from opac_proc.web import config

# #### EXTRACT MODELS


class ExtractCollection(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        """
        Notificamos o modelos com este uuid que tem que ser reprocessado
        """
        try:
            doc = TransformCollection.objects.get(uuid=uuid).first()
        except Exception:
            pass
        else:
            doc['must_reprocess'] = True
            doc.save()

    meta = {
        'collection': 'e_collection'
    }


signals.pre_save.connect(ExtractCollection.pre_save, sender=ExtractCollection)
signals.post_save.connect(ExtractCollection.post_save, sender=ExtractCollection)


class ExtractJournal(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        """
        Notificamos o modelos com este uuid que tem que ser reprocessado
        """
        try:
            doc = TransformJournal.objects.get(uuid=uuid).first()
        except Exception:
            pass
        else:
            doc['must_reprocess'] = True
            doc.save()

    meta = {
        'collection': 'e_journal'
    }


signals.pre_save.connect(ExtractJournal.pre_save, sender=ExtractJournal)
signals.post_save.connect(ExtractJournal.post_save, sender=ExtractJournal)


class ExtractIssue(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        """
        Notificamos o modelos com este uuid que tem que ser reprocessado
        """
        try:
            doc = TransformIssue.objects.get(uuid=uuid).first()
        except Exception:
            pass
        else:
            doc['must_reprocess'] = True
            doc.save()

    meta = {
        'collection': 'e_issue'
    }


signals.pre_save.connect(ExtractIssue.pre_save, sender=ExtractIssue)
signals.post_save.connect(ExtractIssue.post_save, sender=ExtractIssue)


class ExtractArticle(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        """
        Notificamos o modelos com este uuid que tem que ser reprocessado
        """
        try:
            doc = TransformArticle.objects.get(uuid=uuid).first()
        except Exception:
            pass
        else:
            doc['must_reprocess'] = True
            doc.save()

    meta = {
        'collection': 'e_article'
    }


signals.pre_save.connect(ExtractArticle.pre_save, sender=ExtractArticle)
signals.post_save.connect(ExtractArticle.post_save, sender=ExtractArticle)


class ExtractPressRelease(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        """
        Notificamos o modelos com este uuid que tem que ser reprocessado
        """
        try:
            doc = TransformPressRelease.objects.get(uuid=uuid).first()
        except Exception:
            pass
        else:
            doc['must_reprocess'] = True
            doc.save()

    meta = {
        'collection': 'e_press_release'
    }


signals.pre_save.connect(ExtractPressRelease.pre_save, sender=ExtractPressRelease)
signals.post_save.connect(ExtractPressRelease.post_save, sender=ExtractPressRelease)


class ExtractNews(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        """
        Notificamos o modelos com este uuid que tem que ser reprocessado
        """
        try:
            doc = TransformNews.objects.get(uuid=uuid).first()
        except Exception:
            pass
        else:
            doc['must_reprocess'] = True
            doc.save()

    meta = {
        'collection': 'e_news'
    }


signals.pre_save.connect(ExtractNews.pre_save, sender=ExtractNews)
signals.post_save.connect(ExtractNews.post_save, sender=ExtractNews)


# #### TRANFORM MODELS


class TransformCollection(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        """
        Notificamos o modelos com este uuid que tem que ser reprocessado
        """
        try:
            doc = LoadCollection.objects.get(uuid=uuid).first()
        except Exception:
            pass
        else:
            doc['must_reprocess'] = True
            doc.save()

    meta = {
        'collection': 't_collection'
    }


signals.pre_save.connect(TransformCollection.pre_save, sender=TransformCollection)
signals.post_save.connect(TransformCollection.post_save, sender=TransformCollection)


class TransformJournal(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        """
        Notificamos o modelos com este uuid que tem que ser reprocessado
        """
        try:
            doc = LoadJournal.objects.get(uuid=uuid).first()
        except Exception:
            pass
        else:
            doc['must_reprocess'] = True
            doc.save()

    meta = {
        'collection': 't_journal'
    }


signals.pre_save.connect(TransformJournal.pre_save, sender=TransformJournal)
signals.post_save.connect(TransformJournal.post_save, sender=TransformJournal)


class TransformIssue(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        """
        Notificamos o modelos com este uuid que tem que ser reprocessado
        """
        try:
            doc = LoadIssue.objects.get(uuid=uuid).first()
        except Exception:
            pass
        else:
            doc['must_reprocess'] = True
            doc.save()

    meta = {
        'collection': 't_issue'
    }


signals.pre_save.connect(TransformIssue.pre_save, sender=TransformIssue)
signals.post_save.connect(TransformIssue.post_save, sender=TransformIssue)


class TransformArticle(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        """
        Notificamos o modelos com este uuid que tem que ser reprocessado
        """
        try:
            doc = LoadArticle.objects.get(uuid=uuid).first()
        except Exception:
            pass
        else:
            doc['must_reprocess'] = True
            doc.save()

    meta = {
        'collection': 't_article'
    }


signals.pre_save.connect(TransformArticle.pre_save, sender=TransformArticle)
signals.post_save.connect(TransformArticle.post_save, sender=TransformArticle)


class TransformPressRelease(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        """
        Notificamos o modelos com este uuid que tem que ser reprocessado
        """
        try:
            doc = LoadPressRelease.objects.get(uuid=uuid).first()
        except Exception:
            pass
        else:
            doc['must_reprocess'] = True
            doc.save()

    meta = {
        'collection': 't_press_release'
    }


signals.pre_save.connect(TransformPressRelease.pre_save, sender=TransformPressRelease)
signals.post_save.connect(TransformPressRelease.post_save, sender=TransformPressRelease)


class TransformNews(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        """
        Notificamos o modelos com este uuid que tem que ser reprocessado
        """
        try:
            doc = LoadNews.objects.get(uuid=uuid).first()
        except Exception:
            pass
        else:
            doc['must_reprocess'] = True
            doc.save()

    meta = {
        'collection': 't_news'
    }


signals.pre_save.connect(TransformNews.pre_save, sender=TransformNews)
signals.post_save.connect(TransformNews.post_save, sender=TransformNews)


# #### LOAD MODELS


class LoadCollection(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        pass  # não precisa propagar mais

    meta = {
        'collection': 'l_collection'
    }


signals.pre_save.connect(LoadCollection.pre_save, sender=LoadCollection)
signals.post_save.connect(LoadCollection.post_save, sender=LoadCollection)


class LoadJournal(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        pass  # não precisa propagar mais

    meta = {
        'collection': 'l_journal'
    }


signals.pre_save.connect(LoadJournal.pre_save, sender=LoadJournal)
signals.post_save.connect(LoadJournal.post_save, sender=LoadJournal)


class LoadIssue(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        pass  # não precisa propagar mais

    meta = {
        'collection': 'l_issue'
    }


signals.pre_save.connect(LoadIssue.pre_save, sender=LoadIssue)
signals.post_save.connect(LoadIssue.post_save, sender=LoadIssue)


class LoadArticle(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        pass  # não precisa propagar mais

    meta = {
        'collection': 'l_article'
    }


signals.pre_save.connect(LoadArticle.pre_save, sender=LoadArticle)
signals.post_save.connect(LoadArticle.post_save, sender=LoadArticle)


class LoadPressRelease(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        pass  # não precisa propagar mais

    meta = {
        'collection': 'l_press_release'
    }


signals.pre_save.connect(LoadPressRelease.pre_save, sender=LoadPressRelease)
signals.post_save.connect(LoadPressRelease.post_save, sender=LoadPressRelease)


class LoadNews(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        pass  # não precisa propagar mais

    meta = {
        'collection': 'l_news'
    }


signals.pre_save.connect(LoadNews.pre_save, sender=LoadNews)
signals.post_save.connect(LoadNews.post_save, sender=LoadNews)


# #### NOTIFICATIONS

class Message(Document):
    subject = StringField(max_length=50, default='')
    body = StringField(default='')
    stage = StringField(max_length=10, default='default')   # 'extract' | 'transform' | 'load'
    model_name = StringField(max_length=15, default='')     # 'collection' | 'journal' | 'issue' | 'article' | 'pree_release' | 'news'
    created_at = DateTimeField(default=datetime.now)
    unread = BooleanField(required=True, default=True)

    @classmethod  # signal pre_save (asociar em cada modelo)
    def pre_save(cls, sender, document, **kwargs):
        document.created_at = datetime.now()

    meta = {
        'collection': 'messages',
    }

signals.pre_save.connect(Message.pre_save, sender=Message)

# #### LOGS


class ExtractLog(DynamicDocument):
    meta = {
        'max_size': 104857600,  # 100 MB (104857600 Bytes)
        'max_documents': 100000,
        'collection': 'extract_log',
        'db_alias': config.OPAC_PROC_LOG_MONGODB_NAME,
    }


class TransformLog(DynamicDocument):
    meta = {
        'max_size': 104857600,  # 100 MB (104857600 Bytes)
        'max_documents': 100000,
        'collection': 'transform_log',
        'db_alias': config.OPAC_PROC_LOG_MONGODB_NAME,
    }


class LoadLog(DynamicDocument):
    meta = {
        'max_size': 104857600,  # 100 MB (104857600 Bytes)
        'max_documents': 100000,
        'collection': 'load_log',
        'db_alias': config.OPAC_PROC_LOG_MONGODB_NAME,
    }


class DefaultLog(DynamicDocument):
    meta = {
        'max_size': 104857600,  # 100 MB (104857600 Bytes)
        'max_documents': 100000,
        'collection': 'default_log',
        'db_alias': config.OPAC_PROC_LOG_MONGODB_NAME,
    }
