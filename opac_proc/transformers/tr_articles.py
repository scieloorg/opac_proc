# coding: utf-8
import os
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

from opac_proc.core.asset_handler import AssetHandler

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

        # PDFs
        if hasattr(xylose_article, 'xml_languages') or hasattr(xylose_article, 'fulltexts'):

            pdfs = []
            langs = set()

            article_version = xylose_article.data_model_version

            logger.info(u"Artigo PID: %s, ID: %s, tem a versão: %s",
                        pid, uuid, article_version)

            if article_version == 'xml':
                # Devemos coletar somente os idiomas do texto completo.
                if hasattr(xylose_article, 'languages'):
                    for lang in xylose_article.languages():
                        langs.add(lang)
            else:

                if hasattr(xylose_article, 'fulltexts') and \
                   'pdf' in xylose_article.fulltexts().keys():

                    for lang in xylose_article.fulltexts().get('pdf').keys():
                        langs.add(lang)

            logger.info(u"Idiomas existentes no artigo PID: %s, ID: %s, idiomas: %s",
                        pid, uuid, langs)

            for lang in list(langs):
                file_type = 'pdf'

                original_lang = self.transform_model_instance['original_language']

                logger.info(u"Idioma original do artigo PID: %s, ID: %s, original lang: %s",
                            pid, uuid, original_lang)

                if lang == original_lang:
                    prefix = ''
                else:
                    prefix = '%s_' % lang

                file_path = '%s/%s/%s/%s%s.pdf' % (config.OPAC_PROC_ASSETS_SOURCE_PDF_PATH,
                                 xylose_article.journal.acronym.lower(),
                                 xylose_article.assets_code,
                                 prefix,
                                 xylose_article.file_code())

                logger.info(u"Caminho do PDF do artigo com PID: %s e ID: %s, caminho: %s",
                            pid, uuid, file_path)

                try:
                    pfile = open(file_path, 'rb')
                except IOError as e:
                    logger.error(u'Erro ao tentar abri o PDF: %s, do artigo com PID: %s',
                                 file_path, pid)
                    raise Exception(u'Erro ao tentar abri o PDF: %s', file_path)
                else:

                    file_name = os.path.basename(file_path)

                    logger.info(u"Nome do PDF do artigo com PID: %s e ID: %s, nome: %s",
                                pid, uuid, file_name)

                    article_folder = xylose_article.file_code()
                    issue_folder = xylose_article.assets_code
                    journal_folder = xylose_article.journal.acronym.lower()

                    bucket_name = '/'.join([journal_folder, issue_folder])

                    logger.info(u"Bucket name do PDF do artigo com PID: %s e ID: %s, bucket name: %s",
                                pid, uuid, bucket_name)

                    file_meta = {
                                 'article_pid': pid,
                                 'lang': lang,
                                 'bucket_name': bucket_name,
                                 'article_folder': xylose_article.file_code(),
                                 'issue_folder': xylose_article.assets_code,
                                 'journal_folder': xylose_article.journal.acronym.lower(),
                                }

                    asset = AssetHandler(pfile, file_name, file_type, file_meta,
                                         bucket_name)

                    uuid = asset.register()

                    logger.info(u"UUID do artigo com PID: %s e ID: %s, cadastrado no SSM: %s",
                                pid, uuid, uuid)

                    pdfs.append({
                        'type': file_type,
                        'language': lang,
                        'url': asset.get_urls()['url']
                    })

                logger.info(u"PDF cadastrado para o artigo com PID: %s e ID: %s, PDF: %s",
                            pid, uuid, asset.get_urls()['url'])

            self.transform_model_instance['pdfs'] = pdfs

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

        return self.transform_model_instance
