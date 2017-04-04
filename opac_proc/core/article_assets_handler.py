# coding: utf-8

import os

from StringIO import StringIO

from opac_proc.web import config
from opac_proc.transformers import html_generator
from opac_proc.core.asset_handler import AssetHandler
from opac_proc.logger_setup import getMongoLogger


if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "assets")
else:
    logger = getMongoLogger(__name__, "INFO", "assets")


def _pfile(filename):
    try:
        pfile = open(filename, 'rb')
    except Exception as e:
        logger.error(u'Não encontrado {}'.format(filename))
        raise e
    else:
        return pfile


class ArticleSourceFiles(object):
    """
        Handler the article source files such as XML, PDF, HTML files
        and its media files, such as images, videos, supplementary material etc
        Params:
            :param xylose_article: article data returned by xylose api
            :param article_uuid: string article uuid provided by opac proc
    """
    def __init__(self, xylose_article, article_uuid):
        self.xylose_article = xylose_article
        self.issue_folder_name = self.xylose_article.assets_code
        self.journal_folder_name = self.xylose_article.journal.acronym.lower()
        self.article_folder_name = self.xylose_article.file_code()
        self.article_pid = self.xylose_article.publisher_id
        self.article_uuid = article_uuid
        self.registered_media_assets = None

    @property
    def journal_and_issue_folders(self):
        """
        Returns relative path formed by journal folder/issue folder
        """
        return '/'.join([self.journal_folder_name, self.issue_folder_name])

    @property
    def article_metadata(self):
        """
        Returns the article metadata, formed by:
         * article_folder
         * issue_folder
         * journal_folder
         * bucket_name
         * article_pid
         * article_uuid
        """
        metadata = {}
        metadata['article_folder'] = self.article_folder_name
        metadata['issue_folder'] = self.issue_folder_name
        metadata['journal_folder'] = self.journal_folder_name
        metadata['bucket_name'] = self.journal_and_issue_folders
        metadata['article_pid'] = self.article_pid
        metadata['article_uuid'] = self.article_uuid
        return metadata

    @property
    def pdf_folder_path(self):
        """
        Returns the folder path of article PDF files
        """
        return '/'.join([
                config.OPAC_PROC_ASSETS_SOURCE_PDF_PATH,
                self.journal_and_issue_folders])

    @property
    def media_folder_paths(self):
        """
        Returns a list of paths of article media files
        """
        main_path = '/'.join([
                config.OPAC_PROC_ASSETS_SOURCE_MEDIA_PATH,
                self.journal_and_issue_folders])
        return [
                main_path,
                main_path + '/html',
                self.pdf_folder_path]

    @property
    def xml_folder_path(self):
        """
        Returns the folder path of article XML file
        """
        return '/'.join([
                config.OPAC_PROC_ASSETS_SOURCE_XML_PATH,
                self.journal_and_issue_folders])

    @property
    def text_languages(self):
        """
        Returns the list of article text languages
        """
        langs = []
        if hasattr(self.xylose_article, 'fulltexts'):
            langs.extend(self.xylose_article.fulltexts().get('pdf', {}).keys())
        elif self.xylose_article.data_model_version == 'xml':
            langs.extend(self.xylose_article.xml_languages())
        return langs

    @property
    def pdf_filenames(self):
        """
        Returns pairs key, value of {language: PDF file name}
        """
        filenames = {}
        for lang in self.text_languages:
            prefix = '' if lang == self.xylose_article.original_language() else lang+'_'
            filenames[lang] = '{}{}.pdf'.format(
                prefix,
                self.article_folder_name)
        return filenames

    @property
    def pdf_files_data(self):
        """
        Returns PDF files data, formed by pairs of:
         * language
         * tuple (pfile, filename, file metadata)
        """
        files_data = {}
        for lang, filename in self.pdf_filenames.items():
            file_metadata = self.article_metadata.copy()
            file_metadata.update({'lang': lang})
            pfile = _pfile(self.pdf_folder_path + '/' + filename)
            if pfile is not None:
                files_data[lang] = (
                    pfile,
                    filename,
                    file_metadata)
        return files_data

    @property
    def media_files_data(self):
        """
        Returns media files data, formed by pairs of:
         * filename
         * tuple (pfile, filename, file metadata)
        """
        files_data = {}
        for path in self.media_folder_paths:
            if os.path.isdir(path):
                fnames = [fname for fname in os.listdir(path) if fname.startswith(self.article_folder_name)]
                for fname in fnames:
                    if fname not in self.pdf_filenames:
                        pfile = _pfile(path + '/' + fname),
                        pfile = path + '/' + fname
                        if pfile is not None:
                            files_data[fname] = (
                                pfile,
                                fname,
                                self.article_metadata)
        return files_data

    @property
    def xml_fullpath(self):
        """
        Returns full path of XML file, if exists
        """
        if self.xylose_article.data_model_version == 'xml':
            return self.xml_folder_path+'/'+self.article_folder_name+'.xml'

    @property
    def fixed_xml(self):
        """
        Returns fixed XML content, which had the media paths changed
        """
        if self.xml_fullpath is not None:
            _xml = open(self.xml_fullpath, 'rb').read().decode('utf-8')
            if self.registered_media_assets is not None:
                for media_name, url in self.registered_media_assets.items():
                    new_href_content = 'href="{}"'.format(url)
                    href_content = 'href="{}"'.format(media_name)

                    for alternative in [
                        href_content,
                        href_content.replace('.jpg', '.tiff'),
                        href_content.replace('.jpg', '.tif'),
                    ]:
                        _xml = _xml.replace(alternative, new_href_content)
            return StringIO(_xml.encode('utf-8'))

    @property
    def xml_file_data(self):
        """
        Returns XML file info, formed by pairs of:
         * xml
         * tuple (pfile, filename, file metadata)
        """
        if self.fixed_xml is not None:
            return {'xml': (
                self.fixed_xml,
                self.article_folder_name+'.xml',
                self.article_metadata)}

    @property
    def html_filenames(self):
        """
        Returns HTML filenames, formed by pairs of:
         * language
         * HTML filename
        """
        filenames = {}
        for lang in self.text_languages:
            prefix = '' if lang == self.xylose_article.original_language() else lang+'_'
            filenames[lang] = '{}{}.html'.format(
                prefix,
                self.article_folder_name)
        return filenames

    @property
    def html_content_items(self):
        """
        Returns HTML content items, formed by pairs of:
         * language
         * html content
        """
        items = {}
        if self.xml_fullpath is None:
            items = self.xylose_article.translated_htmls() or {}
            items.update(
                {self.xylose_article.original_language():
                    self.xylose_article.original_html()})
            for lang, item in items.items():
                for media_name, url in self.registered_media_assets.items():
                    href_content = 'src="/img/revistas/{}/{}"'.format(
                        self.journal_and_issue_folders,
                        media_name)
                    new_href_content = 'src="{}"'.format(url)
                    item = item.replace(href_content, new_href_content)
                items[lang] = item
        else:
            items = self.generate_htmls()
        return items

    @property
    def html_files_data(self):
        """
        Returns HTML files data, formed by pairs of:
         * language
         * tuple (pfile, filename, file metadata)
        """
        files_data = {}
        for lang, html in self.html_content_items.items():
            file_metadata = self.article_metadata.copy()
            file_metadata.update({'lang': lang})
            if html is not None:
                files_data[lang] = (
                    StringIO(html.encode('utf-8')),
                    self.html_filenames.get(lang),
                    file_metadata)
        return files_data

    def generate_htmls(self):
        """
        Generates HTML contents from XML for all the text languages
        Returns them as pairs of:
         * language
         * HTML content
        """
        if self.fixed_xml is not None:
            htmls, errors = html_generator.generate_htmls(
                self.fixed_xml,
                config.OPAC_PROC_CSS_PATH)
            if errors:
                for error in errors:
                    logger.error(error)
            return htmls


class Assets(object):
    """
        Handler the assets of an article such as XML, PDF, HTML files
        and its media files, such as images, videos, supplementary material etc
        Asks for their registration in a DAM system
        Params:
            :param article_uuid: string article uuid provided by opac proc
            :param xylose_article: article data returned by xylose api
    """

    def __init__(self, article_uuid, xylose_article):
        self.source_files = ArticleSourceFiles(
            xylose_article,
            article_uuid)
        self.pdf_assets = None
        self.registered_pdf_assets = None
        self.xml_assets = None
        self.registered_xml_assets = None
        self.html_assets = None
        self.registered_html_assets = None

    def _register_assets(self, source_files_data):
        """
        Creates assets of a group of source files and
        Asks for their registration in a DAM system.
        Params:
            :param source_files_data: data of source files group
        """
        assets = []
        if source_files_data is not None:
            for label, source_file_data in source_files_data.items():
                pfile, filename, file_metadata = source_file_data
                _, filetype = os.path.splitext(filename)
                if pfile is not None:
                    asset = AssetHandler(
                            pfile,
                            filename,
                            filetype[1:],
                            file_metadata,
                            self.source_files.journal_and_issue_folders)
                    asset.register()
                    assets.append(asset)
                else:
                    logger.error(
                        u'Não foi possível ler o arquivo {} ({} {})'.format(
                            filename,
                            filetype,
                            label if label != filetype else ''))
        return assets

    def _registered_assets_data(self, assets):
        """
        Returns the data of an assets group.
        Params:
            :param assets: group of assets
        """
        data = None
        if assets is not None:
            for asset in assets:
                if asset.url is not None:
                    if asset.metadata.get('lang') is not None:
                        if data is None:
                            data = []
                        data.append({
                            'type': asset.filetype,
                            'language': asset.metadata.get('lang'),
                            'url': asset.url
                        })
                    elif asset.filetype == 'xml':
                        data = asset.url
                    else:
                        if data is None:
                            data = {}
                        data[asset.name] = asset.url
        return data

    def register(self):
        """
        Creates all the assets of an article,
        including for the generated HTML from XML files, if apply, and
        Asks for their registration in a DAM system.
        """
        media_assets = self._register_assets(
            self.source_files.media_files_data)
        self.source_files.registered_media_assets = self._registered_assets_data(
                media_assets)

        self.pdf_assets = self._register_assets(
            self.source_files.pdf_files_data)
        self.registered_pdf_assets = self._registered_assets_data(
            self.pdf_assets)

        self.xml_assets = None
        self.registered_xml_assets = None
        if self.source_files.xml_fullpath is not None:
            self.xml_assets = self._register_assets(
                self.source_files.xml_file_data)
            self.registered_xml_assets = self._registered_assets_data(
                self.xml_assets)

        self.html_assets = self._register_assets(
            self.source_files.html_files_data)
        self.registered_html_assets = self._registered_assets_data(
            self.html_assets)
