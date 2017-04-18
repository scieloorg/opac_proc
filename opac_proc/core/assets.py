# coding: utf-8

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

from ssm_handler import SSMHandler

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "transform")
else:
    logger = getMongoLogger(__name__, "INFO", "transform")


class Assets(object):
    """

    Handler the assets of the article: XML, PDF, HTML and IMGs.

    It receives as parameter a xylose object and knows how to perform the
    necessary treatments of the assets for the DAM and knows the ``metadata``
    needed for each asset.

    Params:
        :param xylose_article: article data returned by xylose api
    """

    def __init__(self, xylose):
        self.xylose = xylose

    def _open_asset(self, file_path):
        """
        Open asset as file like object(bytes)
        """
        try:
            return open(file_path, 'rb')
        except IOError as e:
            logger.error(u'Erro ao tentar abri o ativo: %s, erro: %s',
                         file_path, e)
            raise Exception(u'Erro ao tentar abri o ativo: %s', file_path)

    @property
    def bucket_name(self):
        """
        Reeturn the bucket name to assets
        """

        issue_folder = self.xylose.assets_code
        journal_folder = self.xylose.journal.acronym.lower()

        return '/'.join([journal_folder, issue_folder])

    def get_langs(self):
        """
        This method has as responsibility to obtain the list of languages
        available in the article through the xylose object.

        IMPORTANT: If article is a xml version get the lang from languages
        atribute, otherwise return key of 'pdf' dictionary on fulltexts method.

        Return: the acronym list of languages

        Example: ['es', 'en', ....]
        """

        langs = set()

        if self.xylose.data_model_version == 'xml':
            if hasattr(self.xylose, 'languages'):
                for lang in self.xylose.languages():
                    langs.add(lang)
        else:
            if hasattr(self.xylose, 'fulltexts') and \
                    'pdf' in self.xylose.fulltexts().keys():

                for lang in self.xylose.fulltexts().get('pdf').keys():
                    langs.add(lang)

        logger.info(u"Artigo com PID: %s, tem os seguintes idiomas: %s",
                    self.xylose.publisher_id, langs)

        return list(langs)

    def get_assets(self):
        """
        The rule for translating HTML and PDF assets is to add the language
        prefix as the first follow-up of the file name.

        This method has as responsibility returns the list of assets with
        their respective prefixes.

        IMPORTANT: If article is not a 'XML' version, doesn`t exists any asset
        of full article text. The xylose has translated_htmls() to get the
        content.

        Return: a dict with asset extesion and a list of dict where the key is
        the lang and de value is the asset name with prefix.

        Example:
            {
                'pdf':[
                        {'en': 'en_1413-8123-csc-19-01-00215.pdf'},
                        {'pt': '1413-8123-csc-19-01-00215.pdf'}, # if the lang default
                    ],
                'xml': [
                        {'en': 'en_1413-8123-csc-19-01-00215.xml'},
                        {'pt': '1413-8123-csc-19-01-00215.xml'}, # if the lang default
                    ]
            }
        """

        assets = {}
        pdf_lang = []
        xml_lang = []

        original_lang = self.xylose.original_language()

        file_code = self.xylose.file_code()

        logger.info(u"Idioma original do artigo PID: %s, original lang: %s",
                    self.xylose.publisher_id, original_lang)

        logger.info(self.get_langs())

        for lang in self.get_langs():

            prefix = '' if lang == original_lang else '%s_' % lang

            pdf_lang.append({lang: '{}{}.pdf'.format(prefix, file_code)})
            assets['pdf'] = pdf_lang

            if self.xylose.data_model_version == 'xml':

                xml_lang.append({lang: '{}{}.xml'.format(prefix, file_code)})
                assets['xml'] = xml_lang

        return assets

    def get_metadata(self):
        """
        This method return a dictionary with asset metadata.

        IMPORTANT: To DAM is mandatory two keys: ``pid`` and ``collection``,
        used in exists() ssm_handler
        """
        metadata = {}

        metadata['pid'] = self.xylose.publisher_id
        metadata['collection'] = self.xylose.collection_acronym
        metadata['doi'] = self.xylose.doi
        metadata['issue'] = self.xylose.assets_code
        metadata['file_name'] = self.xylose.file_code()
        metadata['journal'] = self.xylose.journal.acronym.lower()
        metadata['scielo_issn'] = self.xylose.journal.scielo_issn
        metadata['issn'] = self.xylose.journal.any_issn()

        return metadata

    def register_pdf(self):
        """
        Method to register the PDF(s) of the asset.
        """
        logger.info(u"Iniciando o cadasto do(s) PDF(s) do artigo PID: %s",
                    self.xylose.publisher_id)

        file_type = 'pdf'
        pdfs = []

        if 'pdf' not in self.get_assets():
            msg_error = u"Não existe PDF para o artigo PID: %s" % self.xylose.publisher_id
            logger.info(msg_error)
            raise Exception(msg_error)
        else:
            logger.info(u"Lista de PDF(s) existente para o artigo PID: %s",
                        self.xylose.publisher_id)

        for item in self.get_assets().get('pdf'):
            for lang, pdf_name in item.items():
                file_path = '%s/%s/%s/%s' % (
                            config.OPAC_PROC_ASSETS_SOURCE_PDF_PATH,
                            self.xylose.journal.acronym.lower(),
                            self.xylose.assets_code,
                            pdf_name)

                logger.info(u"Caminho do PDF do artigo PID: %s, idioma:%s, %s",
                            self.xylose.publisher_id, lang, file_path)

                pfile = self._open_asset(file_path)

                logger.info(u"Bucket name:%s do PDF: %s", self.bucket_name,
                            file_path)

                metadata = self.get_metadata()
                metadata.update({'lang': lang,
                                 'file_path': file_path,
                                 'bucket_name': self.bucket_name,
                                 'type': file_type})

                ssm_asset = SSMHandler(pfile, pdf_name, file_type, metadata,
                                       self.bucket_name)

                if ssm_asset.exists():
                    logger.info(u"Já existe um PDF com PID: %s e coleção: %s cadastrado",
                                self.xylose.publisher_id, self.xylose.collection_acronym)
                else:
                    uuid = ssm_asset.register()

                    logger.info(u"UUID: %s para o PDF do artigo com PID: %s",
                                uuid, self.xylose.publisher_id)

                    pdfs.append({
                        'type': file_type,
                        'language': lang,
                        'url': ssm_asset.get_urls()['url']
                    })

                    logger.info(u"PDF(s): %s cadastrado(s) para o artigo com PID: %s",
                                pdfs, self.xylose.publisher_id)

        return pdfs
