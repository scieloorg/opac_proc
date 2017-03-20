# code = utf-8

import os

from opac_proc.web import config

"""
Identify the fulltexts locations from xylose, and create the structure:
    xylose:
        For "html"
        "fulltexts": {
            "pdf": {
                "en": "http://www.scielo.br/pdf/rsp/v40n3/en_07.pdf",
                "pt": "http://www.scielo.br/pdf/rsp/v40n3/07.pdf"
                },
            "html": {
                "en": "http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0034-89102006000300007&tlng=en",
                "pt": "http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0034-89102006000300007&tlng=pt"
            }
        }
        For XML:
        data_model_version == 'xml'
        build the pdf url from xml_languages
"""

class SourceTextFile(object):

    def __init__(self, source_location):
        self.source_location = source_location
        self.path = os.path.dirname(source_location)
        self.filename = os.path.basename(source_location)

    @property
    def location(self):
        if os.path.isfile(self.source_location):
            return self.source_location
    

class SourceFiles(object):

    def __init__(self, xylose_article):
        self.xylose_article = xylose_article
        self.issue_folder_name = self.xylose_article.assets_code
        self.journal_folder_name = self.xylose_article.journal.acronym.lower()
        self.article_folder_name = self.xylose_article.file_code()
        self.href_files = {}
        self.setUp()

    def setUp(self):
        self._texts_info = self._get_data_from_sgm_version()
        self._texts_info.update(self._get_data_from_sps_version())
        
    @property
    def bucket_name(self):
        return '-'.join([self.journal_folder_name, self.issue_folder_name, self.article_folder_name])

    @property
    def issue_folder_rel_path(self):
        return '/'.join([self.journal_folder_name, self.issue_folder_name])

    @property
    def article_metadata(self):
        metadata = {}
        metadata['article-folder'] = self.article_folder_name
        metadata['issue-folder'] = self.issue_folder_name
        metadata['journal-folder'] = self.journal_folder_name
        return metadata

    @property
    def pdf_files(self):
        return self._texts_info.get('pdf', {})

    @property
    def pdf_folder_path(self):
        return '/'.join([config.OPAC_PROC_ASSETS_SOURCE_PDF_PATH, self.issue_folder_rel_path])

    def _get_data_from_sgm_version(self):
        fulltext_files = {}
        if hasattr(self.xylose_article, 'fulltexts'):
            pdf_url_items = self.xylose_article.fulltexts().get('pdf')
            fulltext_files['pdf'] = {}
            for lang in pdf_url_items.keys():
                prefix = '' if lang != self.xylose_article.original_language else lang+'_'
                fulltext_files['pdf'][lang] = SourceTextFile('{}/{}{}.pdf'.format(self.pdf_folder_path, prefix, self.article_folder_name))
        return fulltext_files 

    def _get_data_from_sps_version(self):
    	fulltext_files = {}
        if self.xylose_article.data_model_version == 'xml':
            fulltext_files['pdf'] = {}
            if hasattr(self.xylose_article, 'xml_languages'):
                if self.xylose_article.xml_languages() is not None:
                    for lang in self.xylose_article.xml_languages():
                        prefix = '' if lang == self.xylose_article.original_language else lang+'_'
                        fulltext_files['pdf'][lang] = SourceTextFile('{}/{}{}.pdf'.format(self.pdf_folder_path, prefix, self.article_folder_name))
        return fulltext_files

