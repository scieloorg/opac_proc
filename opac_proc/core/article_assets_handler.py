# coding: utf-8

import os

from StringIO import StringIO
from opac_proc.web import config
from opac_proc.transformers import html_generator
from opac_proc.core.asset_handler import AssetHandler


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
        self.generated_htmls_content = None
        self.css_path = css_path
        self.article_uuid = article_uuid
        
    @property
    def bucket_name(self):
        return '-'.join([self.journal_folder_name, self.issue_folder_name, self.article_folder_name])

    @property
    def issue_folder_rel_path(self):
        return '/'.join([self.journal_folder_name, self.issue_folder_name])

    @property
    def article_metadata(self):
        metadata = {}
        metadata['article_folder'] = self.article_folder_name
        metadata['issue_folder'] = self.issue_folder_name
        metadata['journal_folder'] = self.journal_folder_name
        metadata['bucket_name'] = self.bucket_name
        metadata['article_pid'] = self.xylose_article.publisher_id
        metadata['article_uuid'] = self.article_uuid        
        return metadata

    @property
    def pdf_folder_path(self):
        return '/'.join([config.OPAC_PROC_ASSETS_SOURCE_PDF_PATH, self.issue_folder_rel_path])

    @property
    def media_folder_path(self):
        return '/'.join([config.OPAC_PROC_ASSETS_SOURCE_MEDIA_PATH, self.issue_folder_rel_path])

    @property
    def xml_folder_path(self):
        return '/'.join([config.OPAC_PROC_ASSETS_SOURCE_XML_PATH, self.issue_folder_rel_path])

    @property
    def pdf_files(self):
        fulltext_files = {}
        langs = []
        if hasattr(self.xylose_article, 'fulltexts'):
            langs.extend(self.xylose_article.fulltexts().get('pdf', {}).keys())
        elif self.xylose_article.data_model_version == 'xml':
            langs.extend(self.xylose_article.xml_languages())
        for lang in langs:
            prefix = '' if lang == self.xylose_article.original_language else lang+'_'
            file_metadata = self.article_metadata.copy()
            file_metadata.update({'lang': lang})
            fulltext_files[lang] = ('{}/{}{}.pdf'.format(self.pdf_folder_path, prefix, self.article_folder_name), file_metadata)
        return fulltext_files 

    @property
    def media_files(self):
        files = {}
        for path in [self.media_folder_path, self.media_folder_path + '/html']:    
            if os.path.isdir(path):
                files.update({fname: (path + '/' + fname, self.article_metadata) for fname in os.listdir(path) if fname.startswith(self.article_folder_name)})
        return files

    @property
    def xml_file(self):
        if self.xylose_article.data_model_version == 'xml':
            return {'xml': (self.xml_folder_path + '/' + self.article_folder_name + '.xml', self.article_metadata)}

    @property
    def xml_filename(self):
        if self.xylose_article.data_model_version == 'xml':
            return self.xml_folder_path + '/' + self.article_folder_name + '.xml'

    def generate_htmls(self):
        if self.xml_filename is not None:
            self.generated_htmls_content, errors = html_generator.generate_htmls(self.xml_filename, self.css_path)
            return errors


class Assets(object):

    def __init__(self, article_uuid, xylose_article, css_path):
        self.css_path = css_path
        self.source_files = ArticleSourceFiles(xylose_article, article_uuid, css_path)
        self.assets_logs = []
        self.pdf_assets = []
        self.xml_assets = []
        self.media_assets = []
        self.html_assets = []
        self.create_assets(self.pdf_assets, self.source_files.pdf_files, 'pdf')
        self.create_assets(self.media_assets, self.source_files.media_files, '')
        self.create_assets(self.xml_assets, self.source_files.xml_file, 'xml')
        self.assets_items = self.media_assets + self.xml_assets + self.pdf_assets
        
    def pfile(self, filename):
        try:
            _pfile = open(filename, 'rb')
        except Exception, e:            
            pass
        else:
            return _pfile
            
    @property
    def assets_sources(self):
        sources = {}
        sources['pdfs'] = self.source_files.pdf_files.values()
        sources['media'] = self.source_files.media_files.values()
        sources['xml'] = self.source_files.xml_file
        return sources

    def assets_registrations(self):
        return [(asset.uuid, asset.name, asset.registration_status()) for asset in self.assets_items]

    def create_assets(self, assets, source_files, filetype):
        if source_files is not None:
            for label, source_file_data in source_files.items():
                source_file, file_metadata = source_file_data
                pfile = self.pfile(source_file)
                if pfile is not None:
                    assets.append(AssetHandler(pfile, os.path.basename(source_file), filetype, file_metadata, self.source_files.bucket_name))
                else:
                    self.assets_logs.append(u'Não foi possível ler o arquivo {} correspondente a {} {} '.format(source_file, filetype, label if label != filetype else ''))

    def register(self):
        for asset in self.assets_items:
            asset.register_async()

    def is_executing(self, assets_items):
        return '; '.join(['{} ({})'.format(asset.name, asset.uuid) for asset in assets_items if not asset.registration_status() in ('FAILURE', 'SUCCESS')])

    def wait_registration(self, assets_items):
        doing = self.is_executing(assets_items)
        while len(doing) > 0:
            self.assets_logs.append(u'Esperando o registro de {}'.format(doing))
            doing = self.is_executing(assets_items)
            
    def registered_pdf_assets(self):
        data = []
        self.wait_registration(self.pdf_assets)
        for asset in self.pdf_assets:
            if asset.registration_status() == 'SUCCESS':
                data.append({'type': asset.filetype, 
                        'language': asset.metadata.get('lang'),
                        'url': asset.url})
            elif asset.registration_status() == 'FAILURE':
                self.assets_logs.append(u'Falha ao registrar {} {} '.format(asset.uuid, asset.name))
        return data

    def registered_xml_assets(self):
        data = None
        self.wait_registration(self.xml_assets)
        for asset in self.xml_assets:
            if asset.registration_status() == 'SUCCESS':
                data = asset.url
            elif asset.registration_status() == 'FAILURE':
                self.assets_logs.append(u'Falha ao registrar {} {} '.format(asset.uuid, asset.name))
        return data

    def registered_media_assets(self):
        self.wait_registration(self.media_assets)
        return {asset.name: asset.url for asset in self.media_assets}

    def registered_html_assets(self):
        data = []
        self.wait_registration(self.html_assets)
        for asset in self.html_assets:
            if asset.registration_status() == 'SUCCESS':
                data.append({'type': asset.filetype, 
                        'language': asset.metadata.get('lang'),
                        'url': asset.url})
            elif asset.registration_status() == 'FAILURE':
                self.assets_logs.append(u'Falha ao registrar {} {} '.format(asset.uuid, asset.name))
        return data

    def _fix_media_paths(self, replacements=None):
        result = {}
        for lang, content in self.source_files.generated_htmls_content.items():
            if replacements is not None:
                for media_name, url in replacements.items():
                    href_content = 'href="{}"'.format(media_name)
                    ssm_href_content = 'href="{}"'.format(url)
                    content = content.replace(href_content, ssm_href_content)
            try:
                result[lang] = StringIO(content.encode('utf-8'))
            except Exception as e:
                self.assets_logs.append('{}'.format(e))
        return result

    def create_html_assets(self):
        self.html_assets = []
        error = None
        if self.source_files.generated_htmls_content is None:
            error = self.source_files.generate_htmls()
        if error is not None:
            self.assets_logs.extend(error)        
        if self.source_files.generated_htmls_content is not None:
            html_files = self._fix_media_paths(self.registered_media_assets())
            
            for lang, pfile in html_files.items():
                filename = lang+'_'+self.source_files.article_folder_name + '.html'                        
                file_metadata = {'lang': lang}
                file_metadata.update(self.source_files.article_metadata)
                
                if pfile is not None:
                    self.html_assets.append(AssetHandler(pfile, filename, 'html', file_metadata, self.source_files.bucket_name))
                else:
                    self.assets_logs.append(u'Não foi possível ler o arquivo {} correspondente a {} {} '.format(filename, 'html', lang))
            self.assets_items.extend(self.html_assets)

    def register_html_assets(self):
        for asset in self.html_assets:
            asset.register()

