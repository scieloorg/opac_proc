# coding: utf-8
import itertools
import json
import os
import re
from io import BytesIO, open as io_open

from bs4 import BeautifulSoup
from lxml import etree
from packtools import HTMLGenerator

from opac_proc.core import utils
from opac_proc.logger_setup import getMongoLogger
from opac_proc.web import config
from html_generator import generate_htmls
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
        self._content = None

    def _open_asset(self, file_path, mode='rb', encoding=None):
        """
        Open asset as file like object(bytes)
        """
        try:
            if encoding is None:
                return open(file_path, mode)
            else:
                return io_open(file_path, mode, encoding=encoding)

        except IOError as e:
            msg_error = u'Erro ao tentar abri o ativo: %s, erro: %s' % (file_path, e)
            logger.error(msg_error)

            if config.OPAC_PROC_RAISE_ERROR:
                raise Exception(msg_error)
            else:
                return None

    def _change_img_path(self, medias):
        """
        Changes the path of the media in XML so that it is something accessible.
        """

        if medias:
            for media_name, url in medias.items():
                # test media_name is unicode?
                if not isinstance(media_name, unicode):
                    media_name = media_name.encode('utf-8')

                # test url is unicode?
                if not isinstance(url, unicode):
                    url = url.encode('utf-8')

                self._content = self._content.replace(media_name, url)

    def _is_external_link(self, path):
        ext_link_indicators = config.MEDIA_EXT_LINKS_IND.split(',')
        return any(
            map(lambda ext_link_ind: path.startswith(ext_link_ind),
                ext_link_indicators)
        )

    def _extract_media(self):
        """
        Return a list of media to be collect from content

        Try get imgs by xlink:href and src tags with internal links.
        """
        if self.xylose.data_model_version == 'xml':
            msg_error = "Método não deve ser usado para XMLs."
            logger.error(msg_error)
            raise TypeError(msg_error)

        parser = "html.parser"
        soup = BeautifulSoup(self._content, parser)
        src_tags = [
            tag.get('src').strip().encode('utf-8')
            for tag in soup.find_all(src=True)
        ]

        medias = [
            src_tag
            for src_tag in src_tags
            if not self._is_external_link(src_tag)
        ]

        return medias

    def _get_media_path(self, name):
        """
        Returns the folder path of media.
        """
        asset_path = config.OPAC_PROC_ASSETS_SOURCE_MEDIA_PATH
        if os.path.splitext(name)[-1].lower() == '.pdf':
            asset_path = config.OPAC_PROC_ASSETS_SOURCE_PDF_PATH

        return '%s/%s/%s/%s' % (
                            asset_path,
                            self.xylose.journal.acronym.lower(),
                            self.xylose.assets_code,
                            name)

    def _get_langs(self):
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

        msg_info = u"Artigo com PID: %s, tem os seguintes idiomas: %s" % (
            self.xylose.publisher_id, langs)
        logger.info(msg_info)

        return list(langs)

    def _normalize_media_path_html(self, media_path):
        """
        This method takes the path to the media and fits to known paths
        and returns a tuple with the media path in the original html,
        the path known in the file system.

        In addition to making some extrension adjustments

        Params:
            :param media_path: the path to the media.
                Example of paths:
                    /img/revistas/gs/v29n4/original_breve1_t1.jpg (must common example)
                    /img/fbpe/gs/v29n4/original_breve1_t1.jpg
                    ../img/revistas/gs/v29n4/original_breve1_t1.jpg
                    img/revistas/resp/v80n6/seta.gif
                    /img/revistas/resp/v80n6/seta.gif (this media is no registered)
        """

        origin_path = media_path

        # TODO: Colocar um cadastro de mídias fixas para não alterar? Consulta
        # que não seja feita a cada interação para não comprometer performance
        exclude_medias = ['seta.jpg', 'seta.gif']

        if os.path.basename(media_path) in exclude_medias:
            return (origin_path, None)

        source_media_path = config.OPAC_PROC_ASSETS_SOURCE_MEDIA_PATH

        change_media_path = [('tif', 'jpg'), ('../', '/'), ('./', '/'),
                             ('/img/fbpe', source_media_path),
                             ('img/fbpe', source_media_path),
                             ('/img/revistas', source_media_path),
                             ('img/revistas', source_media_path)]

        for _from, _to in change_media_path:
            media_path = media_path.replace(_from, _to.lower())

        return (origin_path, media_path)

    @property
    def bucket_name(self):
        """
        Reeturn the bucket name to assets
        """

        issue_folder = self.xylose.assets_code
        journal_folder = self.xylose.journal.acronym.lower()

        return '/'.join([journal_folder, issue_folder])

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
                'xml': '1413-8123-csc-19-01-00215.xml'
            }
        """

        assets = {}
        pdf_lang = []

        original_lang = self.xylose.original_language()

        file_code = self.xylose.file_code()

        msg_info = u"Idioma original do artigo PID: %s, original lang: %s" % (
            self.xylose.publisher_id, original_lang)
        logger.info(msg_info)

        for lang in self._get_langs():

            prefix = '' if lang == original_lang else '%s_' % lang

            pdf_lang.append({lang: u'{}{}.pdf'.format(prefix, file_code)})
            assets['pdf'] = pdf_lang

        if self.xylose.data_model_version == 'xml':
            assets['xml'] = u'{0}.xml'.format(file_code)
        else:
            # importante verificar se é o xylose devolve uma URL
            pass

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

    def register_media_html(self):
        """
        Return a dictionary with all media added in SSM.

        Example:  {
                    'a08tab01.gif': 'http://ssm.scielo.org/media/assets/resp/v89n1/a08tab01.gif'
                    'a08tab3b.gif': 'http://ssm.scielo.org/media/assets/resp/v89n1/a08tab3b.gif'
                  }
        """
        file_type = 'img'  # Not all are images
        registered_medias = {}

        medias = self._extract_media()

        for media in medias:

            origin_path, media_path = self._normalize_media_path_html(media)

            if not media_path:
                continue

            pfile = self._open_asset(media_path)

            if not pfile:
                continue

            metadata = self.get_metadata()
            metadata.update({'file_path': media_path,
                             'bucket_name': self.bucket_name,
                             'type': file_type,
                             'origin_path': origin_path})

            media_name = os.path.basename(media_path)

            ssm_asset = SSMHandler(pfile, media_name, file_type, metadata,
                                   self.bucket_name)

            code, existing_asset = ssm_asset.exists()

            # Existe mas não é identico (existe com o mesmo nome)
            if code == 2:
                logger.info(u"Já existe um media com PID: %s e colecao: %s, cadastrado: %s",
                            self.xylose.publisher_id, self.xylose.collection_acronym, existing_asset)
                logger.info(u"Lista de imagens com mesmo filename para o artigo com PID: %s, %s",
                            self.xylose.publisher_id, existing_asset)
                logger.info(u"Removendo a lista de images: %s", existing_asset)

                for asset in existing_asset:
                    ssm_asset.remove(asset['uuid'])

            # Existe mas não é idêntico code=2, removido no passo anterior deve ser
            # recadastrado, também deve ser cadastrado caso não exista, code=0.
            if code == 2 or code == 0:
                uuid = ssm_asset.register()

                logger.info(u"UUID: %s para media do artigo com PID: %s",
                            uuid, self.xylose.publisher_id)

                registered_medias.update({origin_path: ssm_asset.get_urls()['url_path']})

                logger.info(u"Medias(s): %s cadastrado(s) para o artigo com PID: %s",
                            registered_medias, self.xylose.publisher_id)

            # Existe e o ativo é idêntico
            if code == 1:
                for asset in existing_asset:
                    metadata = json.loads(asset['metadata'])
                    registered_medias.update({metadata['origin_path']:
                                              asset['absolute_url']})

                logger.info(u"Medias já existente no SSM: %s", registered_medias)

        return registered_medias

    def register(self):
        raise NotImplementedError()


class AssetPDF(Assets):

    def _get_path(self, name):
        """
        Returns the folder path of article PDF(s) file.
        """
        return '%s/%s/%s/%s' % (
                            config.OPAC_PROC_ASSETS_SOURCE_PDF_PATH,
                            self.xylose.journal.acronym.lower(),
                            self.xylose.assets_code,
                            name)

    def register(self):
        """
        Method to register the PDF(s) of the asset.
        """
        logger.info(u"Iniciando o cadastro do(s) PDF(s) do artigo PID: %s",
                    self.xylose.publisher_id)

        pdfs = []
        file_type = 'pdf'

        if 'pdf' not in self.get_assets():
            msg_error = u"Não existe PDF para o artigo PID: %s" % self.xylose.publisher_id

            logger.error(msg_error)

            if config.OPAC_PROC_RAISE_ERROR:
                raise Exception(msg_error)

        else:
            logger.info(u"Lista de PDF(s) existente para o artigo PID: %s",
                        self.get_assets().get('pdf'))

            for item in self.get_assets().get('pdf'):
                for lang, pdf_name in item.items():
                    file_path = self._get_path(pdf_name)

                    logger.info(u"Caminho do PDF do artigo PID: %s, idioma: %s, %s",
                                self.xylose.publisher_id, lang, file_path)

                    pfile = self._open_asset(file_path)

                    # Continue if pfile in None
                    if not pfile:
                        continue

                    logger.info(u"Bucket name: %s do PDF: %s", self.bucket_name,
                                file_path)

                    metadata = self.get_metadata()
                    metadata.update({'lang': lang,
                                     'file_path': file_path,
                                     'bucket_name': self.bucket_name,
                                     'type': file_type})

                    ssm_asset = SSMHandler(pfile, pdf_name, file_type, metadata,
                                           self.bucket_name)

                    code, assets = ssm_asset.exists()

                    logger.info(u"Código de existência do PDF: %s", code)

                    # Existe e o ativo é idêntico
                    if code == 1:
                        logger.info(u"Já existe um PDF idêntico com PID: %s e coleção: %s, cadastrado!",
                                    self.xylose.publisher_id, self.xylose.collection_acronym)

                        pdfs.append({
                            'type': file_type,
                            'lang': lang,
                            'url': assets[0]['full_absolute_url']
                        })

                    # Existe mas não é idêntico (existe com o mesmo nome)
                    if code == 2:
                        logger.info(u"Já existe um PDF não idêntico com PID: %s e coleção: %s, cadastrado!",
                                    self.xylose.publisher_id, self.xylose.collection_acronym)

                        for asset in assets:
                            ssm_asset.remove(asset['uuid'])

                    # Existe mas não é identico code=2, removido no passo anterior deve ser
                    # recadastrado, também deve ser cadastrado caso não exista, code=0.
                    if code == 2 or code == 0:
                        uuid = ssm_asset.register()

                        logger.info(u"UUID: %s para o PDF do artigo com PID: %s",
                                    uuid, self.xylose.publisher_id)

                        pdfs.append({
                            'type': file_type,
                            'lang': lang,
                            'url': ssm_asset.get_urls()['url']
                        })

                logger.info(u"PDF(s): %s cadastrado(s) para o artigo com PID: %s",
                            pdfs, self.xylose.publisher_id)

        if pdfs:
            return pdfs


class AssetXML(Assets):

    def __init__(self, xylose):
        super(AssetXML, self).__init__(xylose)
        self._file_type = self.xylose.data_model_version
        self._file_name = self._get_file_name(self._file_type)
        self._content = self._get_content()

    def _get_file_name(self, file_type, lang=None):
        original_lang = self.xylose.original_language()
        file_code = self.xylose.file_code()
        prefix = ''
        if lang and lang != original_lang:
            prefix = '%s_' % lang

        return u'{}{}.{}'.format(prefix, file_code, file_type)

    def _get_content(self):
        """
        Get XML file content, using etree.parse, reading _file_name path.
        If there is no file_name, it raises an Exception according to config.
        """
        if not self._file_name:
            msg_error = "Não existe {} para o artigo, PID: {}".format(
                self._file_type.upper(), self.xylose.publisher_id)
            logger.error(msg_error)
            if config.OPAC_PROC_RAISE_ERROR:
                raise Exception(msg_error)
            else:
                return None

        logger.info("{} existente para o artigo, PID: {}".format(
            self._file_type.upper(), self._file_name))

        parser = etree.XMLParser(remove_blank_text=True)
        file_path = self._get_path(self._file_name)
        try:
            return etree.parse(file_path, parser)
        except Exception as e:
            msg_error = 'Erro no parser do XML: {}, erro: {}'.format(
                file_path, e)
            logger.error(msg_error)
            if config.OPAC_PROC_RAISE_ERROR:
                raise Exception(msg_error)
            return None

    def _get_path(self, name):
        """
        Returns the folder path of article XML file.
        """
        return '%s/%s/%s/%s' % (
                            config.OPAC_PROC_ASSETS_SOURCE_XML_PATH,
                            self.xylose.journal.acronym.lower(),
                            self.xylose.assets_code,
                            name)

    def _get_media(self):
        """
        Find all media elements in self._content (an etree._Element) and return
        a generator with tuples (element, attrib_key), where element is a media
        tree element and attrib_key is the xlink:href attrib.
        Only media elements with href attrib that contains path with file
        extension in MEDIA_EXTENSION_FILES are returned.
        """
        attribs = [
            './/graphic[@xlink:href]',
            './/media[@xlink:href]',
            './/inline-graphic[@xlink:href]',
            './/supplementary-material[@xlink:href]',
            './/inline-supplementary-material[@xlink:href]',
        ]
        namespaces = {'xlink': 'http://www.w3.org/1999/xlink'}
        attrib_iters = [
            self._content.iterfind(attrib, namespaces=namespaces)
            for attrib in attribs
        ]
        attrib_key = '{http://www.w3.org/1999/xlink}href'
        ext_files_list = [
            '.' + extension
            for extension in config.MEDIA_EXTENSION_FILES.split(',')
        ]
        return (
            (element, attrib_key)
            for element in itertools.chain(*attrib_iters)
            if (os.path.splitext(element.attrib[attrib_key])[-1] in ext_files_list
                and not self._is_external_link(element.attrib[attrib_key]))
        )

    def _register_ssm_media(self, pfile, media_path, file_type, metadata):
        ssm_asset = SSMHandler(pfile, media_path, file_type, metadata,
                               self.bucket_name)
        code, existing_asset = ssm_asset.exists()
        # Existe mas não é idêntico (existe com o mesmo nome)
        if code == 2:
            logger.info(u"Já existe um media com PID: {}".format(
                        self.xylose.publisher_id))
            for asset in existing_asset:
                ssm_asset.remove(asset['uuid'])
        # Existe mas não é identico code=2, removido no passo anterior deve ser
        # recadastrado, também deve ser cadastrado caso não exista, code=0.
        if code == 2 or code == 0:
            uuid = ssm_asset.register()
            logger.info(u"UUID: {} para media do artigo com PID: {}".format(
                        uuid, self.xylose.publisher_id))
            ssm_asset_url = ssm_asset.get_urls()['url_path']
            logger.info(u"Media cadastrada para o artigo: {}".format(
                ssm_asset_url))
        # Existe e o ativo é idêntico
        elif code == 1:
            for asset in existing_asset:
                ssm_asset_url = asset['absolute_url']
            logger.info(u"Medias já existente no SSM: {}".format(ssm_asset_url))
        return ssm_asset_url

    def _normalize_media_path(self, media_path):
        root, ext = os.path.splitext(media_path)
        if ext == '.tif':
            ext = '.jpg'
        return root + ext

    def _register_xml_medias(self):
        file_type = 'img'  # Not all are images

        for element, attrib in self._get_media():
            original_path = element.attrib[attrib]
            media_path = self._normalize_media_path(original_path)

            metadata = self.get_metadata()
            metadata.update({'file_path': media_path,
                             'bucket_name': self.bucket_name,
                             'type': file_type,
                             'origin_path': original_path})

            pfile = self._open_asset(self._get_media_path(media_path))
            if pfile:
                ssm_asset_url = self._register_ssm_media(
                    pfile, media_path, file_type, metadata)
                element.attrib[attrib] = ssm_asset_url

    def _register_ssm_asset(self, pfile, file_name, file_type, metadata):
        ssm_asset = SSMHandler(pfile, file_name, file_type, metadata,
                               self.bucket_name)
        code, assets = ssm_asset.exists()
        if code == 2:
            # Existe o Asset mas não é identico
            logger.info(
                "Já existe {} com PID {} cadastrado mas não é identico".format(
                    file_type.upper(), self.xylose.publisher_id))
            for asset in assets:
                ssm_asset.remove(asset['uuid'])
        if code == 0 or code == 2:
            # Asset não cadastrado ou deletado no passo anterior
            uuid = ssm_asset.register()
            logger.info("UUID: {} para {} do artigo com PID: {}".format(
                    uuid, file_type.upper(), self.xylose.publisher_id))
            logger.info("{} cadastrado".format(file_name))
            return (uuid, ssm_asset.get_urls()['url_path'])
        elif code == 1:
            # Existe o XML e é identico
            logger.info("Já existe um {} com PID {} cadastrado".format(
                    file_type.upper(), self.xylose.publisher_id))
            if assets:
                return (assets[0]['uuid'], assets[0]['full_absolute_url'])

    def register(self):
        """
        Method to register the XML(s) of the asset.

        To register the xml we must replace the path of the image to paths
        valid and registered in SSM.
        """
        logger.info(u"Iniciando o cadasto do XML do artigo PID: {}".format(
                    self.xylose.publisher_id))
        if self._content:
            self._register_xml_medias()     # change self._content

            # passamos de content para bytes
            content_as_bytes = BytesIO(
                etree.tostring(self._content,
                               xml_declaration=True,
                               encoding='utf-8')
            )
            uuid, xml_url = self._register_ssm_asset(content_as_bytes,
                                                     self._file_name,
                                                     self._file_type,
                                                     self.get_metadata())
            return uuid, xml_url

    def register_htmls(self):
        """
        Register HTML contents from XML for all the text languages.
        """
        try:
            generator = HTMLGenerator.parse(
                self._content,
                valid_only=False,
                css=config.OPAC_PROC_ARTICLE_CSS_URL,
                print_css=config.OPAC_PROC_ARTICLE_PRINT_CSS_URL,
                js=config.OPAC_PROC_ARTICLE_JS_URL
            )
        except ValueError as e:
            logger.error('Error getting htmlgenerator: {}.'.format(e.message))
            return None

        registered_htmls = []
        for lang, trans_result in generator:
            html_as_bytes = None
            try:
                html = etree.tostring(trans_result, pretty_print=True,
                                      encoding='utf-8', method='html',
                                      doctype="<!DOCTYPE html>")
                html_as_bytes = BytesIO(html)
            except Exception as e:
                logger.error(
                    'Error converting etree {} to string. '.format(lang))
            else:
                metadata = self.get_metadata()
                metadata.update({'bucket_name': self.bucket_name,
                                 'type': 'html',
                                 'version': 'xml'})
                __, html_url = self._register_ssm_asset(
                    html_as_bytes,
                    self._get_file_name('html', lang),
                    'html',
                    metadata
                )
                registered_htmls.append({
                    'type': 'html',
                    'lang': lang,
                    'url': html_url
                })

        return registered_htmls


class AssetHTMLS(Assets):

    def _get_name(self, lang):

        original_lang = self.xylose.original_language()

        file_code = self.xylose.file_code()

        prefix = '' if lang == original_lang else '%s_' % lang

        return u'{}{}.html'.format(prefix, file_code)

    def generate_htmls(self, content, css=None, print_css=None, js=None):
        """
        Generates HTML contents from XML for all the text languages.
        """
        if not css:
            css = config.OPAC_PROC_ARTICLE_CSS_URL
        if not js:
            js = config.OPAC_PROC_ARTICLE_JS_URL
        if not print_css:
            print_css = config.OPAC_PROC_ARTICLE_PRINT_CSS_URL

        htmls, errors = generate_htmls(content, css, print_css, js)

        if errors:
            for error in errors:
                logger.error("Erro gerando o HTML: %s", error)

        return htmls

    def add_htmls(self, htmls, xml_version=True):
        """
        Method to add html from a dictionary with language as key and the html
        as value.

        Params:
            :param htmls: Dictionary {'lang': 'html'}
            :param version: Indicates whether the html version is xml or not

        Return a list of dictionary with all asset registered.
        """

        registered_htmls = []
        file_type = 'html'

        for lang, html in htmls.items():

            metadata = self.get_metadata()
            metadata.update({'bucket_name': self.bucket_name,
                             'type': file_type,
                             'version': 'html' if not xml_version else 'xml'})

            # Se for versão HTML
            if not xml_version:

                # É necessário fazer o mesmo procedimento que é relizado no XML
                # Cadastrar as medias e alterar o caminho diretamente no HTML

                self._content = html
                registered_media = self.register_media_html()

                logger.info(u"O artigo com PID: %s é uma versão HTML.",
                            self.xylose.publisher_id)

                self._change_img_path(registered_media)  # change self._content

                # Substitui a seta.jpg'
                patterns = config.OPAC_PROC_MEDIA_ARROW_MATCH_REGEXS.split(',')

                arrow = config.OPAC_PROC_MEDIA_ARROW_REPLACE

                for pattern_string in patterns:

                    pattern = re.compile(pattern_string)

                    if re.search(pattern, self._content):
                        self._content = re.sub(pattern, arrow, self._content)

                directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                         'templates')

                html = utils.render_from_template(directory, 'article.html', {
                                                  'html': self._content,
                                                  'css': config.OPAC_PROC_ARTICLE_CSS_URL,
                                                  'css_print': config.OPAC_PROC_ARTICLE_PRINT_CSS_URL
                                                  })
            if isinstance(html, unicode):
                html = html.encode('utf-8')

            # XML or HTML
            ssm_asset = SSMHandler(BytesIO(html), self._get_name(lang), file_type,
                                   metadata, self.bucket_name)

            logger.info(u"Verificando se o asset existe: %s", ssm_asset.exists())

            code, assets = ssm_asset.exists()

            # Existe e o ativo é idêntico
            if code == 1:
                logger.info(u"Já existe um HML idêntico com PID: %s e coleção: %s, cadastrado!",
                            self.xylose.publisher_id, self.xylose.collection_acronym)

                registered_htmls.append({'type': file_type,
                                         'lang': lang,
                                         'url': assets[0]['full_absolute_url']
                                         })

            if code == 2:
                logger.info(u"Já existe um HTML não idêntico com PID: %s e coleção: %s, cadastrado!",
                            self.xylose.publisher_id, self.xylose.collection_acronym)

                for asset in assets:
                    ssm_asset.remove(asset['uuid'])

            if code == 2 or code == 0:
                uuid = ssm_asset.register()

                logger.info(u"UUID: %s para XML/HTML do artigo com PID: %s",
                            uuid, self.xylose.publisher_id)

                registered_htmls.append({'type': file_type,
                                         'lang': lang,
                                         'url': ssm_asset.get_urls()['url']
                                         })

        if registered_htmls:
            return registered_htmls

    def register_from_xml(self, uuid):
        """
        Method to register the HTML(s) of the asset from XML version.

        This method consider if not uuid: It`s a HTML version else: is a XML
        version.

        Params:
            :param uuid: uuid do XML
        """

        ssm_handler = SSMHandler()  # asset handler "vazio"

        exists, asset = ssm_handler.get_asset(uuid)

        if exists:
            generated_htmls = self.generate_htmls(BytesIO(asset['file']))

            return self.add_htmls(generated_htmls)

        else:
            logger.error("XML não existente: %s", asset)

    def register(self):
        """
        Method to register the HTML(s) of the asset from HTML version.
        """
        htmls = {}
        original_html = self.xylose.original_html()
        translated_htmls = self.xylose.translated_htmls()

        if original_html:
            htmls.update({self.xylose.original_language(): original_html})

        if translated_htmls:
            htmls.update(translated_htmls)

        if htmls:
            return self.add_htmls(htmls, False)
        else:
            logger.info(u"Artigo com o PID: %s, não tem HTML",
                        self.xylose.publisher_id)
