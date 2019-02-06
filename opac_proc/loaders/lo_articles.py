# coding: utf-8
from mongoengine.context_managers import switch_db
from mongoengine import DoesNotExist
from mongoengine.queryset.visitor import Q

from opac_proc.datastore.mongodb_connector import get_opac_webapp_db_name
from opac_proc.datastore.identifiers_models import ArticleIdModel

from opac_proc.loaders.base import BaseLoader
from opac_proc.datastore.models import (
    LoadIssue,
    LoadArticle,
    ExtractArticle,
    TransformArticle,
)
from opac_schema.v1.models import Article as OpacArticle
from opac_schema.v1.models import Issue as OpacIssue
from opac_schema.v1.models import Journal as OpacJournal
from opac_schema.v1.models import TranslatedTitle as OpacTranslatedTitle
from opac_schema.v1.models import TranslatedSection as OpacTranslatedSection
from opac_schema.v1.models import ArticleKeyword as OpacArticleKeywords
from opac_schema.v1.models import Abstract as OpacTranslatedAbstracts
from opac_schema.v1.models import AOPUrlSegments as OpacAOPUrlSegments


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

    ids_model_class = ArticleIdModel
    ids_model_name = 'ArticleIdModel'
    ids_model_instance = None

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
        'aop_pid',
        'fpage',
        'fpage_sequence',
        'lpage',
        'elocation',
        'keywords',
        'type',
        'publication_date',
        'xml',
        'aop_url_segs',
    ]

    def remove_aop_records(self):
        logger.debug(u"iniciando remove_aop_records")
        if not hasattr(self.transform_model_instance, 'aop_pid'):
            logger.debug(u"Artigo %s não é ex-ahead"
                         % self.transform_model_instance.pid)
            return
        aop_pid = self.transform_model_instance.aop_pid
        model_class_queryset = [
            (self.ids_model_class, Q(article_pid=aop_pid)),
            (ExtractArticle, Q(code=aop_pid)),
            (self.transform_model_class, Q(pid=aop_pid)),
            (self.load_model_class, Q(loaded_data__pid=aop_pid)),
        ]
        for model_class, queryset in model_class_queryset:
            result = model_class.objects(queryset)
            if not result:
                logger.debug(u"AOP %s não registrado no PROC" % aop_pid)
            else:
                model_instance = result[0]
                logger.info(
                    "Deletando registro do AOP %s, já publicado em fascículo regular"
                    % model_instance.uuid
                )
                model_instance.delete()

        logger.info(
            u"Deletando AOP %s do OPAC, já publicado em fascículo regular"
            % aop_pid
        )
        with switch_db(self.opac_model_class, OPAC_WEBAPP_DB_NAME):
            try:
                opac_article = self.opac_model_class.objects.get(pid=aop_pid)
            except DoesNotExist:
                logger.debug(u"AOP %s não registrado no PROC" % aop_pid)
            else:
                opac_article.delete()

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

    def prepare_aop_url_segs(self):
        logger.debug(u"iniciando prepare_aop_url_segs")
        if not hasattr(self.transform_model_instance, 'aop_pid'):
            logger.info(u"Artigo não é ex-ahead. uuid: %s"
                        % self.transform_model_instance.uuid)
            return None

        logger.debug(u"Artigo é ex-ahead. uuid: %s"
                     % self.transform_model_instance.uuid)

        if hasattr(self.load_model_instance.loaded_data, 'aop_url_segs'):
            logger.debug(u"Ex-ahead com aop_url_segs: %s"
                         % self.load_model_instance.loaded_data.aop_url_segs)
            return OpacAOPUrlSegments(
                **self.load_model_instance.loaded_data.aop_url_segs)

        aop_load_article = self.load_model_class.objects.filter(
            loaded_data__pid=self.transform_model_instance.aop_pid)
        if not aop_load_article:
            logger.info(u"AOP não carregado no sistema. PID: %s"
                        % self.transform_model_instance.aop_pid)
            return None

        url_segs = {
            'url_seg_article': aop_load_article[0].loaded_data.url_segment,
        }
        try:
            opac_issue = LoadIssue.objects.get(
                loaded_data__iid=aop_load_article[0].loaded_data.issue)
        except LoadIssue.DoesNotExist, e:
            logger.error(u"OPAC Issue (_id: %s) não encontrado"
                         % aop_load_article[0].loaded_data.issue)
        else:
            url_segs['url_seg_issue'] = opac_issue.loaded_data.url_segment

        logger.debug(u"OpacAOPUrlSegments: %s" % repr(url_segs))
        return OpacAOPUrlSegments(**url_segs)
