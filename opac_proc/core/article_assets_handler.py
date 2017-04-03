# coding: utf-8

import os

from StringIO import StringIO
from tempfile import NamedTemporaryFile

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


def create_file(content):
    f = NamedTemporaryFile(delete=False)
    # f.name
    try:
        content = content.encode('utf-8')
    except:
        content = content.encode('iso-8859-1')
    f.write(content)
    f.close()
    return f.name


class ArticleSourceFiles(object):
    """
    ArticleSourceFiles
    PDF, XML, Media, HTML files
    """
    def __init__(self, xylose_article, article_uuid, css_path):
        self.xylose_article = xylose_article
        self.issue_folder_name = self.xylose_article.assets_code
        self.journal_folder_name = self.xylose_article.journal.acronym.lower()
        self.article_folder_name = self.xylose_article.file_code()
        self.article_pid = self.xylose_article.publisher_id
        self.css_path = css_path
        self.article_uuid = article_uuid
        self.registered_media_assets = None

    @property
    def issue_folder_rel_path(self):
        return '/'.join([self.journal_folder_name, self.issue_folder_name])

    @property
    def article_metadata(self):
        metadata = {}
        metadata['article_folder'] = self.article_folder_name
        metadata['issue_folder'] = self.issue_folder_name
        metadata['journal_folder'] = self.journal_folder_name
        metadata['bucket_name'] = self.issue_folder_rel_path
        metadata['article_pid'] = self.article_pid
        metadata['article_uuid'] = self.article_uuid
        return metadata

    @property
    def pdf_folder_path(self):
        return '/'.join([
                config.OPAC_PROC_ASSETS_SOURCE_PDF_PATH,
                self.issue_folder_rel_path])

    @property
    def media_folder_path(self):
        return '/'.join([
                config.OPAC_PROC_ASSETS_SOURCE_MEDIA_PATH,
                self.issue_folder_rel_path])

    @property
    def xml_folder_path(self):
        return '/'.join([
                config.OPAC_PROC_ASSETS_SOURCE_XML_PATH,
                self.issue_folder_rel_path])

    @property
    def text_languages(self):
        langs = []
        if hasattr(self.xylose_article, 'fulltexts'):
            langs.extend(self.xylose_article.fulltexts().get('pdf', {}).keys())
        elif self.xylose_article.data_model_version == 'xml':
            langs.extend(self.xylose_article.xml_languages())
        return langs

    @property
    def pdf_filenames(self):
        filenames = {}
        for lang in self.text_languages:
            prefix = '' if lang == self.xylose_article.original_language() else lang+'_'
            filenames[lang] = '{}{}.pdf'.format(
                prefix,
                self.article_folder_name)
        return filenames

    @property
    def pdf_files(self):
        fulltext_files = {'en': '?'}
        for lang, filename in self.pdf_filenames.items():
            file_metadata = self.article_metadata.copy()
            file_metadata.update({'lang': lang})
            pfile = _pfile(self.pdf_folder_path + '/' + filename)
            if pfile is not None:
                fulltext_files[lang] = (
                    pfile,
                    filename,
                    file_metadata)
        return fulltext_files

    @property
    def media_files(self):
        files = {}
        for path in [
                self.media_folder_path,
                self.media_folder_path + '/html',
                self.pdf_folder_path]:
            if os.path.isdir(path):
                fnames = [fname for fname in os.listdir(path) if fname.startswith(self.article_folder_name)]
                for fname in fnames:
                    if fname not in self.pdf_filenames:
                        pfile = _pfile(path + '/' + fname),
                        pfile = path + '/' + fname
                        if pfile is not None:
                            files[fname] = (
                                pfile,
                                fname,
                                self.article_metadata)
        return files

    @property
    def xml_filename(self):
        if self.xylose_article.data_model_version == 'xml':
            return self.xml_folder_path+'/'+self.article_folder_name+'.xml'

    @property
    def xml(self):
        if self.xml_filename is not None:
            _xml = open(self.xml_filename, 'rb')
            if self.registered_media_assets is not None:
                _xml = _xml.read()
                _xml = _xml.decode('utf-8')
                for media_name, url in self.registered_media_assets.items():
                    href_content = 'href="{}"'.format(media_name)
                    new_href_content = 'href="{}"'.format(url)
                    _xml = _xml.replace(href_content, new_href_content)
                _xml = create_file(_xml)
            return _xml

    @property
    def xml_file(self):
        if self.xml is not None:
            return {'xml': (
                self.xml,
                self.article_folder_name+'.xml',
                self.article_metadata)}

    @property
    def html_filenames(self):
        filenames = {}
        for lang in self.text_languages:
            prefix = '' if lang == self.xylose_article.original_language() else lang+'_'
            filenames[lang] = '{}{}.html'.format(
                prefix,
                self.article_folder_name)
        return filenames

    @property
    def html_items(self):
        items = {}
        if self.xml is None:
            items = self.xylose_article.translated_htmls() or {}
            items.update(
                {self.xylose_article.original_language():
                    self.xylose_article.original_html()})
        else:
            items = self.generate_htmls()
        return items

    @property
    def html_files(self):
        files = {}
        for lang, html in self.html_items.items():
            file_metadata = self.article_metadata.copy()
            file_metadata.update({'lang': lang})
            if html is not None:
                files[lang] = (
                    StringIO(html.encode('utf-8')),
                    self.html_filenames.get(lang),
                    file_metadata)
        return files

    def generate_htmls(self):
        if self.xml is not None:
            htmls, errors = html_generator.generate_htmls(
                self.xml,
                self.css_path)
            if errors:
                for error in errors:
                    logger.error(error)
            else:
                os.unlink(self.xml)
            return htmls


class Assets(object):

    def __init__(self, article_uuid, xylose_article, css_path):
        self.css_path = css_path
        self.source_files = ArticleSourceFiles(
            xylose_article,
            article_uuid,
            css_path)

    def _create_assets(self, source_files):
        assets = []
        if source_files is not None:
            for label, source_file_data in source_files.items():
                pfile, filename, file_metadata = source_file_data
                _, filetype = os.path.splitext(filename)
                if pfile is not None:
                    assets.append(
                        AssetHandler(
                            pfile,
                            filename,
                            filetype[1:],
                            file_metadata,
                            self.source_files.issue_folder_rel_path))
                else:
                    logger.error(
                        u'Não foi possível ler o arquivo {} correspondente a {} {} '.format(
                            filename,
                            filetype,
                            label if label != filetype else ''))
        return assets

    def register(self, assets=None):
        media_assets = self._create_assets(self.source_files.media_files)
        for asset in media_assets:
            asset.register()

        self.pdf_assets = self._create_assets(self.source_files.pdf_files)
        for asset in self.pdf_assets:
            asset.register()

        self.xml_assets = None
        if self.source_files.xml_filename is not None:
            self.source_files.registered_media_assets = self._registered_assets_type(media_assets)
            self.xml_assets = self._create_assets(
                self.source_files.xml_file)
            for asset in self.xml_assets:
                asset.register()

        self.html_assets = self._create_assets(self.source_files.html_files)
        for asset in self.html_assets:
            asset.register()

    def _registered_assets_type(self, assets):
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

    def registered_assets(self):
        assets = {}
        assets['pdfs'] = self._registered_assets_type(self.pdf_assets)
        assets['xml'] = self._registered_assets_type(self.xml_assets)
        assets['htmls'] = self._registered_assets_type(self.html_assets)
        return assets
