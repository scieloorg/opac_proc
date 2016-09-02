# coding: utf-8
import logging

from mongoengine.context_managers import switch_db

from opac_proc.datastore.mongodb_connector import get_opac_webapp_db_name
from opac_proc.loaders.base import BaseLoader
from opac_proc.datastore.transform.models import (
    TransformCollection,
    TransformJournal,
    TransformIssue,
    TransformArticle)
from opac_schema.v1.models import Article as OpacArticle
from opac_schema.v1.models import Issue as OpacIssue
from opac_schema.v1.models import Journal as OpacJournal


logger = logging.getLogger(__name__)
OPAC_WEBAPP_DB_NAME = get_opac_webapp_db_name()


class ArticleLoader(BaseLoader):
    transform_model_class = TransformArticle
    transform_model_name = 'TransformArticle'
    transform_model_instance = None

    opac_model_class = OpacArticle
    opac_model_name = 'OpacArticle'
    opac_model_instance = None

    fields_to_load = [
        'aid',
        'issue',
        'journal',
        'title',
        'abstract_languages',
        'sections',
        'section',
        'translated_titles',
        'order',
        'doi',
        'is_aop',
        'created',
        'updated',
        'original_language',
        'languages',
        'abstract',
        'authors',
        'htmls',
        'pdfs',
        'pid',
    ]

    def prepare_issue(self):
        t_issue_uuid = self.transform_model_instance.issue
        print "t_issue_uuid: ", t_issue_uuid
        t_issue_uuid_str = str(t_issue_uuid).replace("-", "")
        print "\tIssue %s do Article %s" % (
            t_issue_uuid_str,
            self.transform_model_instance._id)
        with switch_db(OpacIssue, OPAC_WEBAPP_DB_NAME):
            opac_issue = OpacIssue.objects.get(
                _id=t_issue_uuid_str)
        return opac_issue

    def prepare_journal(self):
        t_journal_uuid = self.transform_model_instance.journal
        t_journal_uuid_str = str(t_journal_uuid).replace("-", "")
        print "\tJournal %s do Article %s" % (
            t_journal_uuid_str,
            self.transform_model_instance._id)
        with switch_db(OpacJournal, OPAC_WEBAPP_DB_NAME):
            opac_journal = OpacJournal.objects.get(
                _id=t_journal_uuid_str)
        return opac_journal
