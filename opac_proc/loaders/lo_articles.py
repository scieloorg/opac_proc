# coding: utf-8
from mongoengine.context_managers import switch_db
from mongoengine import DoesNotExist

from opac_proc.datastore.mongodb_connector import get_opac_webapp_db_name
from opac_proc.loaders.base import BaseLoader
from opac_proc.datastore.models import (
    LoadArticle,
    TransformArticle)
from opac_schema.v1.models import Article as OpacArticle
from opac_schema.v1.models import Issue as OpacIssue
from opac_schema.v1.models import Journal as OpacJournal
from opac_schema.v1.models import TranslatedTitle as OpacTranslatedTitle
from opac_schema.v1.models import TranslatedSection as OpacTranslatedSection
from opac_schema.v1.models import ArticleKeyword as OpacArticleKeywords
from opac_schema.v1.models import Abstract as OpacTranslatedAbstracts


from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "load")
else:
    logger = getMongoLogger(__name__, "INFO", "load")

OPAC_WEBAPP_DB_NAME = get_opac_webapp_db_name()


class ArticleLoader(BaseLoader):
    transform_model_class = TransformArticle
    transform_model_instance = None

    opac_model_class = OpacArticle
    opac_model_instance = None

    load_model_class = LoadArticle
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
        'abstracts',
        'authors',
        'htmls',
        'pdfs',
        'pid',
        'fpage',
        'lpage',
        'elocation',
        'keywords',
        'type',
        'publication_date',
        'xml',
    ]

    def prepare_issue(self):
        logger.debug(u"iniciando prepare_issue")
        t_issue_uuid = self.transform_model_instance.issue
        t_issue_uuid_str = str(t_issue_uuid).replace("-", "")

        try:
            with switch_db(OpacIssue, OPAC_WEBAPP_DB_NAME):
                opac_issue = OpacIssue.objects.get(_id=t_issue_uuid_str)
                logger.debug(u"OPAC Issue: %s (_id: %s) encontrado" % (opac_issue.label, t_issue_uuid_str))
        except DoesNotExist, e:
            logger.error(u"OPAC Issue (_id: %s) não encontrado. Já fez o Load Issue?" % t_issue_uuid_str)
            raise e
        else:
            return opac_issue

    def prepare_journal(self):
        logger.debug(u"iniciando prepare_journal")
        t_journal_uuid = self.transform_model_instance.journal
        t_journal_uuid_str = str(t_journal_uuid).replace("-", "")
        opac_journal = None
        try:
            with switch_db(OpacJournal, OPAC_WEBAPP_DB_NAME):
                opac_journal = OpacJournal.objects.get(_id=t_journal_uuid_str)
                logger.debug(u"OPAC Journal: %s (_id: %s) encontrado" % (opac_journal.acronym, t_journal_uuid_str))
        except DoesNotExist, e:
            logger.error(u"OPAC Journal (_id: %s) não encontrado. Já fez o Load Journal?" % t_journal_uuid_str)
            raise e
        else:
            return opac_journal

    def prepare_translated_titles(self):
        logger.debug(u"iniciando prepare_translated_titles")
        translated_titles = []

        if hasattr(self.transform_model_instance, 'translated_titles'):
            for ttitle in self.transform_model_instance.translated_titles:
                translated_title = OpacTranslatedTitle(**ttitle)
                translated_titles.append(translated_title)
        else:
            logger.info(u"Não existem Translated Titles transformados. uuid: %s" % self.transform_model_instance.uuid)

        logger.debug(u"Translated Titles criados: %s" % len(translated_titles))
        return translated_titles

    def prepare_abstracts(self):
        logger.debug(u"iniciando prepare_abstracts")
        translated_abstracts = []

        if hasattr(self.transform_model_instance, 'abstracts'):
            for trans in self.transform_model_instance.abstracts:
                translated_abstract = OpacTranslatedAbstracts(**trans)
                translated_abstracts.append(translated_abstract)
        else:
            logger.info(u"Não existe resumos transformados para o uuid: %s" % self.transform_model_instance.uuid)

        logger.debug(u"Resumos adicionados: %s" % len(translated_abstracts))
        return translated_abstracts

    def prepare_sections(self):
        logger.debug(u"iniciando prepare_sections")
        sections = []

        if hasattr(self.transform_model_instance, 'sections'):
            for section in self.transform_model_instance.sections:
                opac_section = OpacTranslatedSection(**section)
                sections.append(opac_section)
        else:
            logger.info(u"Não existem Sections transformadas. uuid: %s" % self.transform_model_instance.uuid)

        logger.debug(u"sections criados: %s" % len(sections))
        return sections

    def prepare_keywords(self):
        logger.debug(u"iniciando prepare_keywords")
        keywords = []

        if hasattr(self.transform_model_instance, 'keywords'):
            for keyword in self.transform_model_instance.keywords:
                opac_keyword = OpacArticleKeywords(**keyword)
                keywords.append(opac_keyword)
        else:
            logger.info(u"Não existem Keywords transformadas. uuid: %s" % self.transform_model_instance.uuid)

        logger.debug(u"palavras chaves criadss: %s" % len(keywords))
        return keywords
