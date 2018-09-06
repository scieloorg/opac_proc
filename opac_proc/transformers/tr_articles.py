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

from opac_proc.core.assets import AssetPDF, AssetXML, AssetHTMLS

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
        if hasattr(xylose_article, 'abstracts') and xylose_article.abstracts():
            self.transform_model_instance['abstract_languages'] = xylose_article.abstracts().keys()

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
        if xylose_article.issue.is_ahead_of_print:
            self.transform_model_instance['is_aop'] = True

        # is_ex_aop
        if hasattr(xylose_article, 'publisher_ahead_id'):
            if xylose_article.publisher_ahead_id:
                self.transform_model_instance['aop_pid'] = xylose_article.publisher_ahead_id

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

        # abstracts
        if xylose_article.abstracts():

            translated_abstracts = []

            for lang, text in xylose_article.abstracts().items():
                translated_abstracts.append({
                    'language': lang,
                    'text': text,
                })

            self.transform_model_instance['abstracts'] = translated_abstracts

        # authors
        if hasattr(xylose_article, 'authors') and xylose_article.authors:
            self.transform_model_instance['authors'] = ['%s, %s' % (a['surname'], a['given_names']) for a in xylose_article.authors]

        # PDFs
        if hasattr(xylose_article, 'xml_languages') or hasattr(xylose_article, 'fulltexts'):
            asset_pdf = AssetPDF(xylose_article)

            pdfs = asset_pdf.register()

            if pdfs:
                self.transform_model_instance['pdfs'] = pdfs

        # salvamos typo de artigo na fonte: xml ou html
        if hasattr(xylose_article, 'data_model_version'):
            if xylose_article.data_model_version == 'xml':
                self.transform_model_instance['data_model_version'] = 'xml'
            else:
                self.transform_model_instance['data_model_version'] = 'html'

        asset_html = AssetHTMLS(xylose_article)

        # Versão XML do artigo
        if hasattr(xylose_article, 'data_model_version') and xylose_article.data_model_version == 'xml':
            asset_xml = AssetXML(xylose_article)
            xml_url = asset_xml.register()
            if xml_url:
                self.transform_model_instance['xml'] = xml_url
                self.transform_model_instance['htmls'] = asset_xml.register_htmls()

        # Versão HTML do artigo
        if hasattr(xylose_article, 'data_model_version') and xylose_article.data_model_version != 'xml':
            htmls = asset_html.register()
            if htmls:
                self.transform_model_instance['htmls'] = htmls

        # publication_date
        if hasattr(xylose_article, 'publication_date'):
            self.transform_model_instance['publication_date'] = xylose_article.publication_date

        # type
        if hasattr(xylose_article, 'document_type'):
            self.transform_model_instance['type'] = xylose_article.document_type

        # keywords
        if hasattr(xylose_article, 'keywords'):
            keywords = []

            if xylose_article.keywords():
                for lang, keys in xylose_article.keywords().iteritems():
                    keywords.append({'language': lang,
                                     'keywords': keys})

                self.transform_model_instance['keywords'] = keywords

        # pid
        if hasattr(xylose_article, 'publisher_id'):
            self.transform_model_instance['pid'] = xylose_article.publisher_id

        # fpage
        if hasattr(xylose_article, 'start_page'):
            self.transform_model_instance['fpage'] = xylose_article.start_page

        # fpage_sequence
        if hasattr(xylose_article, 'start_page_sequence'):
            self.transform_model_instance['fpage_sequence'] = \
                                            xylose_article.start_page_sequence

        # lpage
        if hasattr(xylose_article, 'end_page'):
            self.transform_model_instance['lpage'] = xylose_article.end_page

        # elocation
        if hasattr(xylose_article, 'elocation'):
            self.transform_model_instance['elocation'] = xylose_article.elocation

        return self.transform_model_instance
