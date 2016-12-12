# coding: utf-8
from datetime import datetime

from werkzeug.urls import url_fix
from xylose.scielodocument import Article

from opac_proc.datastore.models import (
    ExtractArticle,
    TransformArticle,
    TransformIssue,
    TransformJournal)
from opac_proc.transformers.base import BaseTransformer
from opac_proc.transformers.utils import trydate
from opac_proc.extractors.decorators import update_metadata

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

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
        if hasattr(xylose_article, 'languages'):
            lang_set = set(xylose_article.languages() + getattr(self.transform_model_instance, 'abstract_languages', []))
            self.transform_model_instance['languages'] = list(lang_set)

        # abstract
        if hasattr(xylose_article, 'original_abstract'):
            self.transform_model_instance['abstract'] = xylose_article.original_abstract()

        # authors
        if hasattr(xylose_article, 'authors') and xylose_article.authors:
            self.transform_model_instance['authors'] = ['%s, %s' % (a['surname'], a['given_names']) for a in xylose_article.authors]

        # fulltexts -> pdfs, htmls
        if hasattr(xylose_article, 'fulltexts'):
            htmls = []
            pdfs = []
            for text, val in xylose_article.fulltexts().items():
                if text == 'html':
                    for lang, url in val.items():
                        htmls.append({
                            'type': 'html',
                            'language': lang,
                            'url': url_fix(url)
                        })
                elif text == 'pdf':
                    for lang, url in val.items():
                        pdfs.append({
                            'type': 'pdf',
                            'language': lang,
                            'url': url_fix(url)
                        })

            self.transform_model_instance['htmls'] = htmls
            self.transform_model_instance['pdfs'] = pdfs

        # pid
        if hasattr(xylose_article, 'publisher_id'):
            self.transform_model_instance['pid'] = xylose_article.publisher_id

        return self.transform_model_instance
