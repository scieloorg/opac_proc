# code = utf-8

import os
import urllib2

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

    def __init__(self, source_location, journal_folder_name, issue_folder_name, article_folder_name, filename):
        self.source_location = source_location
        self.journal_folder_name = journal_folder_name
        self.issue_folder_name = issue_folder_name
        self.article_folder_name = article_folder_name
        self.filename = filename
        self.is_generated = False

    @property
    def article_folder_path(self):
        return '/'.join([config.ASSETS_SOURCE_PATH, self.journal_folder_name, self.issue_folder_name, self.article_folder_name])

    @property
    def location(self):
        if os.path.isfile(self.source_location):
            return self.source_location
        if os.path.isfile(self.article_folder_path + '/' + self.filename):
            return self.article_folder_path + '/' + self.filename
        if self.source_location.startswith('http'):
            if download(self.source_location, self.article_folder_path + '/' + self.filename):
                self.is_generated = True
                return self.article_folder_path + '/' + self.filename
    
    def delete(self):
        if self.is_generated:
            if os.path.isfile(self.location):
                try:
                    os.unlink(self.location)
                except:
                    pass


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
    def article_metadata(self):
        metadata = {}
        metadata['article-folder'] = self.article_folder_name
        metadata['issue-folder'] = self.issue_folder_name
        metadata['journal-folder'] = self.journal_folder_name
        return metadata

    @property
    def pdf_files(self):
        return self._texts_info.get('pdf', {})

    def fullpath(self, folders):
        return '/'.join([folder for folder in folders if folder is not None])

    @property
    def pdf_folder_path(self):
        return self.fullpath([config.ASSETS_SOURCE_PDF_PATH, self.journal_folder_name, self.issue_folder_name])

    def _get_data_from_sgm_version(self):
        fulltext_files = {}
        if hasattr(self.xylose_article, 'fulltexts'):
            for fileformat, versions in self.xylose_article.fulltexts().items():
                fulltext_files[fileformat] = {}
                for lang, url in versions.items():
                    if not lang in fulltext_files[fileformat].keys():
                        prefix = ''
                        if lang != self.xylose_article.original_language:
                            prefix = lang+'_'
                        fulltext_files[fileformat][lang] = SourceTextFile(
                            url, 
                            self.pdf_folder_path, 
                            prefix + self.article_folder_name + '.' + fileformat)
        return fulltext_files 

    def _get_data_from_sps_version(self):
    	fulltext_files = {}
        if self.xylose_article.data_model_version == 'xml':
            fulltext_files['pdf'] = {}
            if hasattr(self.xylose_article, 'xml_languages'):
                if self.xylose_article.xml_languages() is not None:
                    for lang in self.xylose_article.xml_languages():
                        prefix = '' if lang == self.xylose_article.original_language else lang+'_'
                        url = self.pdf_former_url(prefix)
                        fulltext_files['pdf'][lang] = SourceTextFile(url, self.pdf_folder_path, prefix+self.article_folder_name+'.pdf')
        return fulltext_files

    def pdf_former_url(self, lang_prefix):
        if self.xylose_article.scielo_domain:
            return "http://{}/pdf/{}/{}/{}".format(
                    self.xylose_article.scielo_domain,
                    self.journal_folder_name,
                    self.issue_folder_name,
                    lang_prefix + self.article_folder_name + '.pdf'
            )


def get_web_page_content(url, timeout=30):
    response = None
    req = urllib2.Request(url)
    error_message = ''
    try:
        response = urllib2.urlopen(req, timeout=timeout).read()
    except urllib2.HTTPError as e:
        if e.code == 407:
        error_message = e.read()
    except urllib2.URLError as e:
        error_message = 'URLError'
    except urllib2.socket.timeout:
        error_message = 'Time out!'
    except Exception as e:
        error_message = 'Unknown!'
    return (response, error_message)


def download(url, fullpath):
    content, error_message = get_web_page_content(url)
    if content is not None:
        path = os.path.dirname(fullpath)
        if not os.path.isdir(path):
            os.makedirs(path)
        
        open(fullpath, 'wb').write(content)
    return os.path.isfile(fullpath)

