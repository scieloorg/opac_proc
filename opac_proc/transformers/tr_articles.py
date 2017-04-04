# coding: utf-8
from datetime import datetime

from xylose.scielodocument import Article

from opac_proc.datastore.models import (
    ExtractArticle,
    TransformArticle,
    TransformIssue,
    TransformJournal)
from opac_proc.transformers.base import BaseTransformer
from opac_proc.extractors.decorators import update_metadata

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

from opac_proc.core.article_assets_handler import Assets

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "transform")
else:
    logger = getMongoLogger(__name__, "INFO", "transform")


class ArticleTransformer(BaseTransformer):
    extract_model_class = ExtractArticle
    extract_model_instance = None

    transform_model_class = TransformArticle
    transform_model_instance = None

    def get_extract_model_instance(self, key):
        # retornamos uma instancia de ExtractJounal
        # buscando pela key (=issn)
        return self.extract_model_class.objects.get(code=key)

    @update_metadata
    def transform(self):
        xylose_source = self.clean_for_xylose()
        xylose_article = Article(xylose_source)

        # assets
        assets = Assets(
            str(self.extract_model_instance.uuid),
            xylose_article)
        assets.register()

        # aid
        uuid = self.extract_model_instance.uuid
        self.transform_model_instance['uuid'] = uuid
        self.transform_model_instance['aid'] = uuid

        # issue
        pid = xylose_article.issue.publisher_id
        try:
            issue = TransformIssue.objects.get(pid=pid)
        except Exception, e:
            logger.error(u"TransformIssue (pid: %s) não encontrado!")
            raise e
        else:
            self.transform_model_instance['issue'] = issue.uuid

        # journal
        acronym = xylose_article.journal.acronym
        try:
            journal = TransformJournal.objects.get(acronym=acronym)
        except Exception, e:
            logger.error(u"TransformJournal (acronym: %s) não encontrado!")
            raise e
        else:
            self.transform_model_instance['journal'] = journal.uuid

        # title
        if hasattr(xylose_article, 'original_title'):
            self.transform_model_instance['title'] = xylose_article.original_title()

        # abstract_languages
        if hasattr(xylose_article, 'translated_abstracts') and xylose_article.translated_abstracts():
            self.transform_model_instance['abstract_languages'] = xylose_article.translated_abstracts().keys()

        # translated_sections
        if hasattr(xylose_article, 'translated_section') and xylose_article.translated_section():
            translated_sections = []

            for lang, title in xylose_article.translated_section().items():
                translated_sections.append({
                    'language': lang,
                    'name': title,
                })
            self.transform_model_instance['sections'] = translated_sections

        # section
        if hasattr(xylose_article, 'original_section'):
            self.transform_model_instance['section'] = xylose_article.original_section()

        # translated_titles
        if xylose_article.translated_titles():
            translated_titles = []

            for lang, title in xylose_article.translated_titles().items():
                translated_titles.append({
                    'language': lang,
                    'name': title,
                })

            self.transform_model_instance['translated_titles'] = translated_titles

        # order
        try:
            self.transform_model_instance['order'] = int(xylose_article.order)
        except ValueError, e:
            logger.error(u'xylose_article.order inválida: %s-%s' % (e, xylose_article.order))

        # doi
        if hasattr(xylose_article, 'doi'):
            self.transform_model_instance['doi'] = xylose_article.doi

        # is_aop
        if hasattr(xylose_article, 'is_aop'):
            self.transform_model_instance['is_aop'] = xylose_article.is_aop

        # created
        self.transform_model_instance['created'] = datetime.now()

        # updated
        self.transform_model_instance['updated'] = datetime.now()

        # original_language
        if hasattr(xylose_article, 'original_language'):
            self.transform_model_instance['original_language'] = xylose_article.original_language()

        # languages
        # IMPORTANTE: nesse trecho estamos cadastrando todos os idiomas do texto e do resumo.
        if hasattr(xylose_article, 'languages'):
            lang_set = set(xylose_article.languages() + getattr(self.transform_model_instance, 'abstract_languages', []))
            self.transform_model_instance['languages'] = list(lang_set)

        # abstract
        if hasattr(xylose_article, 'original_abstract'):
            self.transform_model_instance['abstract'] = xylose_article.original_abstract()

        # authors
        if hasattr(xylose_article, 'authors') and xylose_article.authors:
            self.transform_model_instance['authors'] = ['%s, %s' % (a['surname'], a['given_names']) for a in xylose_article.authors]

        # pid
        if hasattr(xylose_article, 'publisher_id'):
            self.transform_model_instance['pid'] = xylose_article.publisher_id

        # fpage
        if hasattr(xylose_article, 'start_page'):
            self.transform_model_instance['fpage'] = xylose_article.start_page

        # lpage
        if hasattr(xylose_article, 'end_page'):
            self.transform_model_instance['lpage'] = xylose_article.end_page

        # elocation
        if hasattr(xylose_article, 'elocation'):
            self.transform_model_instance['elocation'] = xylose_article.elocation

        # assets - consulta os dados registrados dos ativos
        self.transform_model_instance['pdfs'] = assets.registered_pdf_assets
        self.transform_model_instance['xml'] = assets.registered_xml_assets
        self.transform_model_instance['htmls'] = assets.registered_html_assets
        return self.transform_model_instance
