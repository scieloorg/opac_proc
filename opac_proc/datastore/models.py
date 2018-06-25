# coding: utf-8
from datetime import datetime
from mongoengine import (
    Document,
    DynamicDocument,
    EmbeddedDocumentField,
    signals,
    StringField,
    DateTimeField,
    BooleanField,
)
from base_mixin import BaseMixin, LoadedData

from opac_proc.web import config
from opac_proc.datastore import identifiers_models
from opac_proc.source_sync.utils import (
    parse_journal_issn_from_issue_code,
    parse_journal_issn_from_article_code,
    parse_issue_pid_from_article_code,
)


# #### EXTRACT MODELS


class ExtractCollection(BaseMixin, DynamicDocument):
    def update_reprocess_field(self, uuid):
        """
        Notificamos o modelos com este uuid que tem que ser reprocessado
        """
        try:
            doc = TransformCollection.objects.get(uuid=uuid)
        except Exception:
            pass
        else:
            doc['metadata']['must_reprocess'] = True
            doc.save()

    def update_identifier_model(self, uuid, execution_datetime):
        try:
            doc = identifiers_models.CollectionIdModel.objects.get(uuid=uuid)
        except identifiers_models.CollectionIdModel.DoesNotExist:
            pass
        else:
            doc.extract_execution_date = execution_datetime
            doc.save()

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um CollectionDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': self.acronym,
        }

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
            doc = TransformJournal.objects.get(uuid=uuid)
        except Exception:
            pass
        else:
            doc['metadata']['must_reprocess'] = True
            doc.save()

    def update_identifier_model(self, uuid, execution_datetime):
        try:
            doc = identifiers_models.JournalIdModel.objects.get(uuid=uuid)
        except identifiers_models.JournalIdModel.DoesNotExist as e:
            raise e
        else:
            doc.extract_execution_date = execution_datetime
            doc.save()

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um JournalDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': self.collection,
            'journal_issn': self.code
        }

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
            doc = TransformIssue.objects.get(uuid=uuid)
        except Exception:
            pass
        else:
            doc['metadata']['must_reprocess'] = True
            doc.save()

    def update_identifier_model(self, uuid, execution_datetime):
        try:
            doc = identifiers_models.IssueIdModel.objects.get(uuid=uuid)
        except identifiers_models.IssueIdModel.DoesNotExist:
            pass
        else:
            doc.extract_execution_date = execution_datetime
            doc.save()

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um IssueDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': self.collection,
            'journal_issn': parse_journal_issn_from_issue_code(self.code),
            'issue_pid': self.code
        }

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
            doc = TransformArticle.objects.get(uuid=uuid)
        except Exception:
            pass
        else:
            doc['metadata']['must_reprocess'] = True
            doc.save()

    def update_identifier_model(self, uuid, execution_datetime):
        try:
            doc = identifiers_models.ArticleIdModel.objects.get(uuid=uuid)
        except identifiers_models.ArticleIdModel.DoesNotExist:
            pass
        else:
            doc.extract_execution_date = execution_datetime
            doc.save()

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um ArticleDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': self.collection,
            'journal_issn': parse_journal_issn_from_article_code(self.code),
            'issue_pid': parse_issue_pid_from_article_code(self.code),
            'article_pid': self.code
        }

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
            doc = TransformPressRelease.objects.get(uuid=uuid)
        except Exception:
            pass
        else:
            doc['metadata']['must_reprocess'] = True
            doc.save()

    def update_identifier_model(self, uuid, execution_datetime):
        try:
            doc = identifiers_models.PressReleaseIdModel.objects.get(uuid=uuid)
        except identifiers_models.PressReleaseIdModel.DoesNotExist:
            pass
        else:
            doc.extract_execution_date = execution_datetime
            doc.save()

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um NewsDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': config.OPAC_PROC_COLLECTION,
            'url_id': self.url_id
        }

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
            doc = TransformNews.objects.get(uuid=uuid)
        except Exception:
            pass
        else:
            doc['metadata']['must_reprocess'] = True
            doc.save()

    def update_identifier_model(self, uuid, execution_datetime):
        try:
            doc = identifiers_models.NewsIdModel.objects.get(uuid=uuid)
        except identifiers_models.NewsIdModel.DoesNotExist:
            pass
        else:
            doc.extract_execution_date = execution_datetime
            doc.save()

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um NewsDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': config.OPAC_PROC_COLLECTION,
            'url_id': self.url_id
        }

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
            doc = LoadCollection.objects.get(uuid=uuid)
        except Exception:
            pass
        else:
            doc['metadata']['must_reprocess'] = True
            doc.save()

    def update_identifier_model(self, uuid, execution_datetime):
        try:
            doc = identifiers_models.CollectionIdModel.objects.get(uuid=uuid)
        except identifiers_models.CollectionIdModel.DoesNotExist:
            pass
        else:
            doc.transform_execution_date = execution_datetime
            doc.save()

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um CollectionDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': self.acronym,
        }

    meta = {
        'collection': 't_collection'
    }


signals.pre_save.connect(TransformCollection.pre_save, sender=TransformCollection)
signals.post_save.connect(TransformCollection.post_save, sender=TransformCollection)


class TransformJournal(BaseMixin, DynamicDocument):

    @property
    def get_issn(self):
        if hasattr(self, 'scielo_issn'):
            issn = self.scielo_issn
        elif hasattr(self, 'eletronic_issn'):
            issn = self.eletronic_issn
        elif hasattr(self, 'print_issn'):
            issn = self.print_issn
        else:
            raise ValueError('O modelo de Journal com uuid: %s não tem ISSN' % self.uuid)
        return issn

    def update_reprocess_field(self, uuid):
        """
        Notificamos o modelos com este uuid que tem que ser reprocessado
        """
        try:
            doc = LoadJournal.objects.get(uuid=uuid)
        except Exception:
            pass
        else:
            doc['metadata']['must_reprocess'] = True
            doc.save()

    def update_identifier_model(self, uuid, execution_datetime):
        try:
            doc = identifiers_models.JournalIdModel.objects.get(uuid=uuid)
        except identifiers_models.JournalIdModel.DoesNotExist as e:
            raise e
        else:
            doc.transform_execution_date = execution_datetime
            doc.save()

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um JournalDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': self.collection,
            'journal_issn': self.get_issn
        }

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
            doc = LoadIssue.objects.get(uuid=uuid)
        except Exception:
            pass
        else:
            doc['metadata']['must_reprocess'] = True
            doc.save()

    def update_identifier_model(self, uuid, execution_datetime):
        try:
            doc = identifiers_models.IssueIdModel.objects.get(uuid=uuid)
        except identifiers_models.IssueIdModel.DoesNotExist:
            pass
        else:
            doc.transform_execution_date = execution_datetime
            doc.save()

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um IssueDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': config.OPAC_PROC_COLLECTION,
            'journal_issn': parse_journal_issn_from_issue_code(self.pid),
            'issue_pid': self.pid
        }

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
            doc = LoadArticle.objects.get(uuid=uuid)
        except Exception:
            pass
        else:
            doc['metadata']['must_reprocess'] = True
            doc.save()

    def update_identifier_model(self, uuid, execution_datetime):
        try:
            doc = identifiers_models.ArticleIdModel.objects.get(uuid=uuid)
        except identifiers_models.ArticleIdModel.DoesNotExist:
            pass
        else:
            doc.transform_execution_date = execution_datetime
            doc.save()

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um ArticleDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': config.OPAC_PROC_COLLECTION,
            'journal_issn': parse_journal_issn_from_article_code(self.pid),
            'issue_pid': parse_issue_pid_from_article_code(self.pid),
            'article_pid': self.pid
        }

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
            doc = LoadPressRelease.objects.get(uuid=uuid)
        except Exception:
            pass
        else:
            doc['metadata']['must_reprocess'] = True
            doc.save()

    def update_identifier_model(self, uuid, execution_datetime):
        try:
            doc = identifiers_models.PressReleaseIdModel.objects.get(uuid=uuid)
        except identifiers_models.PressReleaseIdModel.DoesNotExist:
            pass
        else:
            doc.transform_execution_date = execution_datetime
            doc.save()

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um NewsDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': config.OPAC_PROC_COLLECTION,
            'url_id': self.url
        }

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
            doc = LoadNews.objects.get(uuid=uuid)
        except Exception:
            pass
        else:
            doc['metadata']['must_reprocess'] = True
            doc.save()

    def update_identifier_model(self, uuid, execution_datetime):
        try:
            doc = identifiers_models.NewsIdModel.objects.get(uuid=uuid)
        except identifiers_models.NewsIdModel.DoesNotExist:
            pass
        else:
            doc.transform_execution_date = execution_datetime
            doc.save()

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um NewsDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': config.OPAC_PROC_COLLECTION,
            'url_id': self.url
        }

    meta = {
        'collection': 't_news'
    }


signals.pre_save.connect(TransformNews.pre_save, sender=TransformNews)
signals.post_save.connect(TransformNews.post_save, sender=TransformNews)


# #### LOAD MODELS


class LoadCollection(BaseMixin, DynamicDocument):
    loaded_data = EmbeddedDocumentField(LoadedData)

    def update_reprocess_field(self, uuid):
        pass  # não precisa propagar mais

    def update_identifier_model(self, uuid, execution_datetime):
        try:
            doc = identifiers_models.CollectionIdModel.objects.get(uuid=uuid)
        except identifiers_models.CollectionIdModel.DoesNotExist:
            pass
        else:
            doc.load_execution_date = execution_datetime
            doc.save()

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um CollectionDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': self.loaded_data.acronym,
        }

    meta = {
        'collection': 'l_collection'
    }


signals.pre_save.connect(LoadCollection.pre_save, sender=LoadCollection)
signals.post_save.connect(LoadCollection.post_save, sender=LoadCollection)


class LoadJournal(BaseMixin, DynamicDocument):
    loaded_data = EmbeddedDocumentField(LoadedData)

    @property
    def get_issn(self):
        if hasattr(self, 'loaded_data'):
            loaded_data = self.loaded_data
        else:
            raise ValueError('O modelo de Journal com uuid: %s não tem loaded_data' % self.uuid)

        if hasattr(loaded_data, 'scielo_issn'):
            issn = loaded_data.scielo_issn
        elif hasattr(loaded_data, 'eletronic_issn'):
            issn = loaded_data.eletronic_issn
        elif hasattr(loaded_data, 'print_issn'):
            issn = loaded_data.print_issn
        else:
            raise ValueError('O modelo de Journal com uuid: %s não tem ISSN' % self.uuid)
        return issn

    def update_reprocess_field(self, uuid):
        pass  # não precisa propagar mais

    def update_identifier_model(self, uuid, execution_datetime):
        try:
            doc = identifiers_models.JournalIdModel.objects.get(uuid=uuid)
        except identifiers_models.JournalIdModel.DoesNotExist as e:
            raise e
        else:
            doc.load_execution_date = execution_datetime
            doc.save()

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um JournalDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': self.loaded_data.collection,
            'journal_issn': self.get_issn
        }

    meta = {
        'collection': 'l_journal'
    }


signals.pre_save.connect(LoadJournal.pre_save, sender=LoadJournal)
signals.post_save.connect(LoadJournal.post_save, sender=LoadJournal)


class LoadIssue(BaseMixin, DynamicDocument):
    loaded_data = EmbeddedDocumentField(LoadedData)

    def update_reprocess_field(self, uuid):
        pass  # não precisa propagar mais

    def update_identifier_model(self, uuid, execution_datetime):
        try:
            doc = identifiers_models.IssueIdModel.objects.get(uuid=uuid)
        except identifiers_models.IssueIdModel.DoesNotExist:
            pass
        else:
            doc.load_execution_date = execution_datetime
            doc.save()

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um IssueDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': config.OPAC_PROC_COLLECTION,
            'journal_issn': parse_journal_issn_from_issue_code(self.loaded_data.pid),
            'issue_pid': self.loaded_data.pid
        }

    meta = {
        'collection': 'l_issue'
    }


signals.pre_save.connect(LoadIssue.pre_save, sender=LoadIssue)
signals.post_save.connect(LoadIssue.post_save, sender=LoadIssue)


class LoadArticle(BaseMixin, DynamicDocument):
    loaded_data = EmbeddedDocumentField(LoadedData)

    def update_reprocess_field(self, uuid):
        pass  # não precisa propagar mais

    def update_identifier_model(self, uuid, execution_datetime):
        try:
            doc = identifiers_models.ArticleIdModel.objects.get(uuid=uuid)
        except identifiers_models.ArticleIdModel.DoesNotExist:
            pass
        else:
            doc.load_execution_date = execution_datetime
            doc.save()

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um ArticleDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': config.OPAC_PROC_COLLECTION,
            'journal_issn': parse_journal_issn_from_article_code(self.loaded_data.pid),
            'issue_pid': parse_issue_pid_from_article_code(self.loaded_data.pid),
            'article_pid': self.loaded_data.pid
        }

    meta = {
        'collection': 'l_article'
    }


signals.pre_save.connect(LoadArticle.pre_save, sender=LoadArticle)
signals.post_save.connect(LoadArticle.post_save, sender=LoadArticle)


class LoadPressRelease(BaseMixin, DynamicDocument):
    loaded_data = EmbeddedDocumentField(LoadedData)

    def update_reprocess_field(self, uuid):
        pass  # não precisa propagar mais

    def update_identifier_model(self, uuid, execution_datetime):
        try:
            doc = identifiers_models.PressReleaseIdModel.objects.get(uuid=uuid)
        except identifiers_models.PressReleaseIdModel.DoesNotExist:
            pass
        else:
            doc.load_execution_date = execution_datetime
            doc.save()

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um NewsDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': config.OPAC_PROC_COLLECTION,
            'url_id': self.url
        }

    meta = {
        'collection': 'l_press_release'
    }


signals.pre_save.connect(LoadPressRelease.pre_save, sender=LoadPressRelease)
signals.post_save.connect(LoadPressRelease.post_save, sender=LoadPressRelease)


class LoadNews(BaseMixin, DynamicDocument):
    loaded_data = EmbeddedDocumentField(LoadedData)

    def update_reprocess_field(self, uuid):
        pass  # não precisa propagar mais

    def update_identifier_model(self, uuid, execution_datetime):
        try:
            doc = identifiers_models.NewsIdModel.objects.get(uuid=uuid)
        except identifiers_models.NewsIdModel.DoesNotExist:
            pass
        else:
            doc.load_execution_date = execution_datetime
            doc.save()

    @property
    def get_diff_model_data(self):
        """
        Retona um dicionariom com a informação dos campos para criarar um NewsDiffModel
        """
        return {
            'uuid': self.uuid,
            'collection_acronym': config.OPAC_PROC_COLLECTION,
            'url_id': self.url
        }

    meta = {
        'collection': 'l_news'
    }


signals.pre_save.connect(LoadNews.pre_save, sender=LoadNews)
signals.post_save.connect(LoadNews.post_save, sender=LoadNews)


# #### NOTIFICATIONS

message_type_choices = [
    'DEFAULT',
    'ERROR',
    'WARNING',
    'INFO',
    'DEBUG',
]


class Message(Document):
    subject = StringField(max_length=128, default='')
    body = StringField(default='')
    stage = StringField(max_length=10, default='default')   # 'extract' | 'transform' | 'load'
    model_name = StringField(max_length=15, default='')     # 'collection' | 'journal' | 'issue' | 'article' | 'pree_release' | 'news'
    created_at = DateTimeField(default=datetime.now)
    unread = BooleanField(required=True, default=True)
    msg_type = StringField(max_length=7, required=True, choices=message_type_choices)

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
