# coding: utf-8
from uuid import uuid4
from mongoengine.context_managers import switch_db

from opac_proc.datastore.mongodb_connector import get_opac_webapp_db_name
from opac_proc.loaders.base import BaseLoader
from opac_proc.datastore.models import (
    LoadArticle,
    TransformCollection,
    TransformJournal,
    TransformIssue,
    TransformArticle)
from opac_schema.v1.models import Article as OpacArticle
from opac_schema.v1.models import Issue as OpacIssue
from opac_schema.v1.models import Journal as OpacJournal
from opac_schema.v1.models import Resource as OpacResource
from opac_schema.v1.models import TranslatedTitle as OpacTranslatedTitle
from opac_schema.v1.models import TranslatedSection as OpacTranslatedSection


from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "transform")
else:
    logger = getMongoLogger(__name__, "INFO", "transform")

OPAC_WEBAPP_DB_NAME = get_opac_webapp_db_name()


class ArticleLoader(BaseLoader):
    transform_model_class = TransformArticle
    transform_model_name = 'TransformArticle'
    transform_model_instance = None

    opac_model_class = OpacArticle
    opac_model_name = 'OpacArticle'
    opac_model_instance = None

    load_model_class = LoadArticle
    load_model_name = 'LoadArticle'
    load_model_instance = None

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
        t_issue_uuid_str = str(t_issue_uuid).replace("-", "")

        with switch_db(OpacIssue, OPAC_WEBAPP_DB_NAME):
            opac_issue = OpacIssue.objects.get(
                _id=t_issue_uuid_str)
        return opac_issue

    def prepare_journal(self):
        t_journal_uuid = self.transform_model_instance.journal
        t_journal_uuid_str = str(t_journal_uuid).replace("-", "")

        with switch_db(OpacJournal, OPAC_WEBAPP_DB_NAME):
            opac_journal = OpacJournal.objects.get(
                _id=t_journal_uuid_str)
        return opac_journal

    def prepare_htmls(self):
        htmls_resources = []
        if hasattr(self.transform_model_instance, 'htmls'):
            with switch_db(OpacResource, OPAC_WEBAPP_DB_NAME):
                for html in self.transform_model_instance.htmls:
                    resource = OpacResource(**html)
                    resource._id = str(uuid4().hex)
                    resource.save()
                    htmls_resources.append(resource)
        return htmls_resources

    def prepare_pdfs(self):
        pdfs_resources = []
        if hasattr(self.transform_model_instance, 'pdfs'):
            with switch_db(OpacResource, OPAC_WEBAPP_DB_NAME):
                for pdf in self.transform_model_instance.pdfs:
                    resource = OpacResource(**pdf)
                    resource._id = str(uuid4().hex)
                    resource.save()
                    pdfs_resources.append(resource)
        return pdfs_resources

    def prepare_translated_titles(self):
        translated_titles = []
        if hasattr(self.transform_model_instance, 'translated_titles'):
            for ttitle in self.transform_model_instance.translated_titles:
                translated_title = OpacTranslatedTitle(**ttitle)
                translated_titles.append(translated_title)
        return translated_titles

    def prepare_sections(self):
        sections = []
        if hasattr(self.transform_model_instance, 'sections'):
            for section in self.transform_model_instance.sections:
                opac_section = OpacTranslatedSection(**section)
                sections.append(opac_section)
        return sections
