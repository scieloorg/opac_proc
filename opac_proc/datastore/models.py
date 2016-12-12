# coding: utf-8
from mongoengine import DynamicDocument, signals, DoesNotExist
from base_mixin import BaseMixin


# #### EXTRACT MODELS


class ExtractCollection(BaseMixin, DynamicDocument):

    def update_reprocess_field(self, uuid):
        """
        Notificamos o modelos com este uuid que tem que ser reprocessado
        """
        try:
            doc = TransformCollection.objects.get(uuid=uuid).first()
        except Exception, e:
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
        except Exception, e:
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
        except Exception, e:
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
        except Exception, e:
            pass
        else:
            doc['must_reprocess'] = True
            doc.save()

    meta = {
        'collection': 'e_article'
    }
signals.pre_save.connect(ExtractArticle.pre_save, sender=ExtractArticle)
signals.post_save.connect(ExtractArticle.post_save, sender=ExtractArticle)

# #### TRANFORM MODELS


class TransformCollection(BaseMixin, DynamicDocument):

    def update_reprocess_field(self, uuid):
        """
        Notificamos o modelos com este uuid que tem que ser reprocessado
        """
        try:
            doc = LoadCollection.objects.get(uuid=uuid).first()
        except Exception, e:
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
        except Exception, e:
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
        except Exception, e:
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
        except Exception, e:
            pass
        else:
            doc['must_reprocess'] = True
            doc.save()

    meta = {
        'collection': 't_article'
    }
signals.pre_save.connect(TransformArticle.pre_save, sender=TransformArticle)
signals.post_save.connect(TransformArticle.post_save, sender=TransformArticle)


# #### LOAD MODELS


class LoadCollection(BaseMixin, DynamicDocument):
    meta = {
        'collection': 'l_collection'
    }
signals.pre_save.connect(LoadCollection.pre_save, sender=LoadCollection)
signals.post_save.connect(LoadCollection.post_save, sender=LoadCollection)


class LoadJournal(BaseMixin, DynamicDocument):
    meta = {
        'collection': 'l_journal'
    }
signals.pre_save.connect(LoadJournal.pre_save, sender=LoadJournal)
signals.post_save.connect(LoadJournal.post_save, sender=LoadJournal)


class LoadIssue(BaseMixin, DynamicDocument):
    meta = {
        'collection': 'l_issue'
    }
signals.pre_save.connect(LoadIssue.pre_save, sender=LoadIssue)
signals.post_save.connect(LoadIssue.post_save, sender=LoadIssue)


class LoadArticle(BaseMixin, DynamicDocument):
    meta = {
        'collection': 'l_article'
    }
signals.pre_save.connect(LoadArticle.pre_save, sender=LoadArticle)
signals.post_save.connect(LoadArticle.post_save, sender=LoadArticle)


# #### LOGS


class ExtractLog(DynamicDocument):
    meta = {
        'collection': 'extract_log',
        'db_alias': 'opac_proc_logs',
    }


class TransformLog(DynamicDocument):
    meta = {
        'collection': 'transform_log',
        'db_alias': 'opac_proc_logs',
    }


class LoadLog(DynamicDocument):
    meta = {
        'collection': 'load_log',
        'db_alias': 'opac_proc_logs',
    }


class DefaultLog(DynamicDocument):
    meta = {
        'collection': 'default_log',
        'db_alias': 'opac_proc_logs',
    }
