# coding: utf-8
import json
import os
from datetime import datetime
from io import BytesIO
from unittest import skip

from bs4 import BeautifulSoup
from lxml import etree
from mock import patch, call
from xylose.scielodocument import Article

from base import BaseTestCase
from opac_proc.core.assets import Assets, AssetXML, AssetHTMLS
from opac_proc.core.ssm_handler import SSMHandler
from opac_proc.web import config


XML_TEST_CONTENT = """<?xml version="1.0" encoding="utf-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink">
    <body>
        <graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf01.tif"/>
    	<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf02.tif"/>
    	<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf03.tif"/>
    	<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf04.tif"/>
    	<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf05.tif"/>
    	<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf06.tif"/>
    	<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf07.tif"/>
    </body>
</article>"""

ssm_in_memory = {}


class MockedXyloseJournal:
    def __init__(self):
        self.acronym = u'test'
        self.scielo_issn = u'0101-0101'

    def any_issn(self):
        return u'0101-0101'


class MockedXyloseArticle:
    def __init__(self):
        self.collection_acronym = u'scl'
        self.journal = MockedXyloseJournal()
        self.assets_code = u'v2n1'
        self.data_model_version = 'xml'
        self.doi = u'10.2564/0101-01012018000100001'
        self.publisher_id = u'S0101-01012018000100001'

    def original_language(self, *kwargs):
        return u'es'

    def file_code(self, *kwargs):
        return u'xml_file'


class SSMHandlerStub(SSMHandler):

    def __init__(self, pfile=None, filename=None, filetype=None, metadata=None,
                 bucket_name=None, attempts=5, sleep_attempts=2):
        """SSM handler Stub."""
        self.pfile = pfile
        self.name = filename
        self.filetype = filetype
        self.metadata = metadata or {}
        self.bucket_name = bucket_name
        self.uuid = None
        self.attempts = attempts
        self.sleep_attempts = sleep_attempts

    def exists(self):
        if ssm_in_memory:
            asset = ssm_in_memory.get(self._checksum_sha256)
            if asset:
                return 1, [asset]
            else:
                assets_by_filename = [
                    asset
                    for asset in ssm_in_memory.values()
                    if asset['filename'] == self.name
                ]
                if assets_by_filename:
                    return 2, assets_by_filename
                return 0, []
        else:
            return 0, []

    def remove(self):
        ssm_in_memory.clear()

    def get_asset(self, uuid):
        return ssm_in_memory

    def register(self):
        self.metadata['registration_date'] = datetime.now().isoformat()
        self.uuid = '123456789-123456789'
        url_path = u'media/assets/{}/{}'.format(self.bucket_name,
                                                self.name)
        asset = {
            'uuid': self.uuid,
            'pfile': self.pfile,
            'filename': self.name,
            'filetype': self.filetype,
            'metadata': self.metadata,
            'bucket_name': self.bucket_name,
            'absolute_url': url_path,
            'full_absolute_url': '{}/{}'.format('ssm.scielo.org', url_path)
        }
        ssm_in_memory.update({self._checksum_sha256: asset})
        return self.uuid

    def get_urls(self):
        return {
            'url_path': u'media/assets/{}/{}'.format(self.bucket_name,
                                                     self.name)
        }


class TestAssets(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        try:
            fixtures_path = os.path.join(os.path.dirname(__file__), 'fixtures')
            article_file_path = os.path.join(fixtures_path,
                                             'article.json')
            cls._json_file = open(article_file_path)
            cls._article_json = cls._json_file.read()
            cls._article_xml = os.path.join(fixtures_path,
                                            '1851-8265-scol-14-01-51.xml')
        except Exception:
            pass

    @classmethod
    def tearDownClass(cls):
        cls._json_file.close()

    def setUp(self):
        self.mocked_xylose_article = MockedXyloseArticle()
        self.xml_content = etree.fromstring(
            XML_TEST_CONTENT,
            etree.XMLParser(remove_blank_text=True)
        )
        ssm_in_memory.clear()

    def test_article_transform_html_extract_media(self):
        self.mocked_xylose_article.data_model_version = 'html'
        asset = AssetHTMLS(self.mocked_xylose_article)
        asset._content = """
        <!-- <img src="/img/revistas/aabc/v76n4/a01img00.gif " /> -->
        <p align="center"><img src="/img/revistas/aabc/v76n4/a01img26.gif " /></p>
        <p><font size="2" face="verdana"> Here, <img src="/img/revistas/aabc/v76n4/a01img27.gif" align="absmiddle" />,<font face="symbol">    \xbc</font>, <img src="/img/revistas/aabc/v76n4/a01img28.gif" align="absmiddle" />    are the eigenvalues of <i>A</i> = \x96<i>dg</i>, where <i>g</i> : <i>M<sup>n</sup></i>    <font face="symbol">\xae</font> <i>S<sup>n</sup></i>(1) is the Gauss map of the    hypersurface. Reilly showed that orientable hypersurfaces with <i>S<sub>r</sub></i><sub>+1</sub>    = 0 are critical points of the functional </font></p>     <p align="center"><img src="/img/revistas/aabc/v76n4/a01img01.gif " /></p>
        """
        html_soup = BeautifulSoup(asset._content, "html.parser")
        expected = [
            img.get('src').strip().encode('utf-8')
            for img in html_soup.find_all(src=True)
        ]
        medias = asset._extract_media()
        self.assertEqual(len(medias), 4)
        self.assertEqual(medias, expected)

    def test_article_transform_html_extract_media_external_links(self):
        self.mocked_xylose_article.data_model_version = 'html'
        asset = AssetHTMLS(self.mocked_xylose_article)
        asset._content = """
        <!-- <img src="/img/revistas/aabc/v76n4/a01img00.gif " /> -->
        <p align="center"><img src="/img/revistas/aabc/v76n4/a01img26.gif " /></p>
        <p>Here, <img src="/img/revistas/aabc/v76n4/a01img27.gif" align="absmiddle" />
            <font face="symbol">    \xbc</font>,
            <img src="https://mail.google.com/mail.gif" align="absmiddle" />
            <font face="symbol">\xae</font>
        </p>
        <p align="center"><img src="/img/revistas/aabc/v76n4/a01img01.gif " /></p>
        """
        expected = [
            "/img/revistas/aabc/v76n4/a01img26.gif",
            "/img/revistas/aabc/v76n4/a01img27.gif",
            "/img/revistas/aabc/v76n4/a01img01.gif"
        ]
        medias = asset._extract_media()
        self.assertEqual(len(medias), 3)
        self.assertEqual(medias, expected)

    @patch.object(AssetXML, '_get_content')
    def test_extract_media_error_if_article_version_xml(self, mocked_get_content):
        mocked_get_content.return_value = self.xml_content
        asset = AssetXML(self.mocked_xylose_article)
        with self.assertRaises(TypeError) as exc_info:
            asset._extract_media()
        self.assertEqual(
            exc_info.exception.message, "Método não deve ser usado para XMLs.")

    def test_normalize_media_path_html_exclude_medias(self):
        asset = Assets(self.mocked_xylose_article)
        media_path = '/img/revistas/gs/v29n4/seta.jpg'
        result = asset._normalize_media_path_html(media_path)
        self.assertIsNotNone(result)
        self.assertEqual(result, (media_path, None))

    def test_normalize_media_path_html_tif_to_jpg(self):
        asset = Assets(self.mocked_xylose_article)
        media_path = '/img/revistas/gs/v29n4/asset.tif'
        expected = '%s/gs/v29n4/asset.jpg' % (
            config.OPAC_PROC_ASSETS_SOURCE_MEDIA_PATH
        )
        original_path, new_media_path = \
            asset._normalize_media_path_html(media_path)
        self.assertIsNotNone(new_media_path)
        self.assertEqual(original_path, media_path)
        self.assertEqual(new_media_path, expected)

    def test_normalize_media_path_html_replace_to_source_media_path(self):
        asset = Assets(self.mocked_xylose_article)
        media_path = '/img/fbpe/gs/v29n4/asset.gif'
        expected = '%s/gs/v29n4/asset.gif' % (
            config.OPAC_PROC_ASSETS_SOURCE_MEDIA_PATH
        )
        original_path, new_media_path = \
            asset._normalize_media_path_html(media_path)
        self.assertIsNotNone(new_media_path)
        self.assertEqual(original_path, media_path)
        self.assertEqual(new_media_path, expected)

    def test_get_media_path_returns_source_media_path(self):
        asset = Assets(self.mocked_xylose_article)
        name = 'asset.jpg'
        expected = '%s/%s/%s/%s' % (config.OPAC_PROC_ASSETS_SOURCE_MEDIA_PATH,
                                    self.mocked_xylose_article.journal.acronym,
                                    self.mocked_xylose_article.assets_code,
                                    name)
        media_path = asset._get_media_path(name)
        self.assertIsNotNone(media_path)
        self.assertEqual(media_path, expected)

    def test_get_media_path_returns_source_pdf_path_for_pdf_files(self):
        asset = Assets(self.mocked_xylose_article)
        name = 'asset.pdf'
        expected = '%s/%s/%s/%s' % (config.OPAC_PROC_ASSETS_SOURCE_PDF_PATH,
                                    self.mocked_xylose_article.journal.acronym,
                                    self.mocked_xylose_article.assets_code,
                                    name)
        media_path = asset._get_media_path(name)
        self.assertIsNotNone(media_path)
        self.assertEqual(media_path, expected)

    @patch.object(AssetXML, '_get_file_name')
    def test_AssetXML_set_file_type_and_name(
        self,
        mocked_get_file_name
    ):
        asset_xml = AssetXML(self.mocked_xylose_article)
        self.assertEqual(asset_xml._file_type,
                         self.mocked_xylose_article.data_model_version)
        mocked_get_file_name.assert_called_once_with(asset_xml._file_type)

    @patch.object(AssetXML, 'get_assets')
    def test_AssetXML_set_content_error_if_there_is_no_xml_asset(
        self,
        mocked_get_assets
    ):
        mocked_get_assets.return_value = {}
        asset_xml = AssetXML(self.mocked_xylose_article)
        self.assertIsNone(asset_xml._content)

    @patch.object(etree, 'parse')
    def test_AssetXML_get_content_file_not_found(
        self,
        mocked_etree_parse
    ):
        mocked_etree_parse.side_effect = Exception('File not found!')
        asset_xml = AssetXML(self.mocked_xylose_article)
        self.assertIsNone(asset_xml._content)

    @patch.object(AssetXML, '_get_content')
    def test_xml_get_media(self, mocked_get_content):
        mocked_get_content.return_value = self.xml_content
        asset = AssetXML(self.mocked_xylose_article)
        expected = [
            "1414-431X-bjmbr-1414-431X20176177-gf01.tif",
            "1414-431X-bjmbr-1414-431X20176177-gf02.tif",
            "1414-431X-bjmbr-1414-431X20176177-gf03.tif",
            "1414-431X-bjmbr-1414-431X20176177-gf04.tif",
            "1414-431X-bjmbr-1414-431X20176177-gf05.tif",
            "1414-431X-bjmbr-1414-431X20176177-gf06.tif",
            "1414-431X-bjmbr-1414-431X20176177-gf07.tif"
        ]
        for count, media in enumerate(asset._get_media()):
            element, attrib_key = media
            self.assertEqual(element.attrib[attrib_key], expected[count])

    @patch.object(AssetXML, '_get_content')
    def test_xml_get_media_valid_extensions(
        self,
        mocked_get_content
    ):
        xml_test_content = """<?xml version="1.0" encoding="utf-8"?>
        <article xmlns:xlink="http://www.w3.org/1999/xlink">
            <body>
                <graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf01.tif"/>
                <graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf02.jpg"/>
                <graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf03.gif"/>
                <graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf04"/>
                <graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf05.doc"/>
                <graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf06.avi"/>
                <graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf07.xls"/>
            </body>
        </article>"""
        mocked_get_content.return_value = etree.fromstring(
            xml_test_content, etree.XMLParser(remove_blank_text=True))

        asset = AssetXML(self.mocked_xylose_article)
        expected = [
            "1414-431X-bjmbr-1414-431X20176177-gf01.tif",
            "1414-431X-bjmbr-1414-431X20176177-gf02.jpg",
            "1414-431X-bjmbr-1414-431X20176177-gf03.gif",
            "1414-431X-bjmbr-1414-431X20176177-gf06.avi",
        ]
        medias = [
            element.attrib[attrib_key]
            for element, attrib_key in asset._get_media()
        ]
        self.assertEqual(len(medias), 4)
        self.assertEqual(medias, expected)

    @patch.object(AssetXML, '_get_content')
    def test_xml_get_media_doenst_return_external_links(
        self,
        mocked_get_content
    ):
        xml_test_content = """<?xml version="1.0" encoding="utf-8"?>
        <article xmlns:xlink="http://www.w3.org/1999/xlink">
            <body>
                <graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf01.tif"/>
                <graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf02.jpg"/>
                <graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf03.gif"/>
                <graphic xlink:href="https://external.link.com/img.png"/>
                <graphic xlink:href="ftp://external.link.com/img.png"/>
                <graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf06.avi"/>
                <graphic xlink:href="http://external.link.com/img.png"/>
            </body>
        </article>"""
        mocked_get_content.return_value = etree.fromstring(
            xml_test_content, etree.XMLParser(remove_blank_text=True))

        asset = AssetXML(self.mocked_xylose_article)
        expected = [
            "1414-431X-bjmbr-1414-431X20176177-gf01.tif",
            "1414-431X-bjmbr-1414-431X20176177-gf02.jpg",
            "1414-431X-bjmbr-1414-431X20176177-gf03.gif",
            "1414-431X-bjmbr-1414-431X20176177-gf06.avi",
        ]
        medias = [
            element.attrib[attrib_key]
            for element, attrib_key in asset._get_media()
        ]
        self.assertEqual(len(medias), 4)
        self.assertEqual(medias, expected)

    def test_normalize_media_path_returns_normalized_path(self):
        asset_xml = AssetXML(self.mocked_xylose_article)
        input_expected = [
            ("graphic.tif", "graphic.jpg"),
            ("image.gif", "image.gif"),
            ("table", "table"),
            ("abc/v21n4/graphic.tif", "abc/v21n4/graphic.jpg")
        ]
        for input, expected in input_expected:
            media_path = asset_xml._normalize_media_path(input)
            self.assertEqual(media_path, expected)

    def setup_register_xml_medias_tests(self):
        self.medias_bytes = [BytesIO(str(n)) for n in range(7)]
        self.filenames = [
            "1414-431X-bjmbr-1414-431X20176177-gf0{}.jpg".format(count)
            for count in range(1, 8)
        ]

    def generate_metadata(self, filename, asset_xml):
        metadata = asset_xml.get_metadata()
        metadata.update({
            'origin_path': os.path.splitext(filename)[0] + '.tif',
            'file_path': filename,
            'bucket_name': asset_xml.bucket_name,
            'type': 'img'
        })
        return metadata

    @patch('opac_proc.core.assets.SSMHandler')
    def test_register_ssm_media_error_if_sss_handler_exception(
        self,
        MockedSSMHandler
    ):
        MockedSSMHandler.side_effect = Exception()
        asset_xml = AssetXML(self.mocked_xylose_article)
        with self.assertRaises(Exception):
            asset_xml._register_ssm_media()

    @patch.object(SSMHandler, 'exists')
    def test_register_ssm_media_error_if_handler_method_exception(
        self,
        mocked_ssmhandler_exists
    ):
        mocked_ssmhandler_exists.side_effect = Exception()
        asset_xml = AssetXML(self.mocked_xylose_article)
        with self.assertRaises(Exception):
            asset_xml._register_ssm_media()

    @patch.object(SSMHandler, 'exists')
    @patch.object(SSMHandler, 'remove')
    @patch.object(SSMHandler, 'register')
    @patch.object(SSMHandler, 'get_urls')
    def test_register_ssm_media_register_if_ssm_asset_doesnt_exist(
        self,
        mocked_ssmhandler_get_urls,
        mocked_ssmhandler_register,
        mocked_ssmhandler_remove,
        mocked_ssmhandler_exists
    ):
        mocked_ssmhandler_exists.return_value = (0, [])
        mocked_ssmhandler_get_urls.return_value = {
            'url': u'http://ssm.scielo.org/media/assets/4853/filename_t8krr12',
            'url_path': u'/media/assets/4853/filename_t8krr12'
        }
        asset_xml = AssetXML(self.mocked_xylose_article)
        result = asset_xml._register_ssm_media(
            BytesIO('1'),
            'image.jpg',
            'img',
            self.generate_metadata('image.jpg', asset_xml)
        )
        mocked_ssmhandler_remove.assert_not_called()
        mocked_ssmhandler_register.assert_called_once()
        self.assertEqual(u'/media/assets/4853/filename_t8krr12', result)

    @patch.object(SSMHandler, 'exists')
    @patch.object(SSMHandler, 'remove')
    @patch.object(SSMHandler, 'register')
    @patch.object(SSMHandler, 'get_urls')
    def test_register_ssm_media_returns_existing_ssm_asset_url(
        self,
        mocked_ssmhandler_get_urls,
        mocked_ssmhandler_register,
        mocked_ssmhandler_remove,
        mocked_ssmhandler_exists
    ):
        mocked_ssmhandler_exists.return_value = (
            1,
            [{
                'uuid': '1234-1234',
                'url': u'http://ssm.scielo.org/media/assets/4853/filename_t8krr12',
                'absolute_url': u'http://ssm.scielo.org/media/assets/4853/t8krr12'
            }])
        asset_xml = AssetXML(self.mocked_xylose_article)
        result = asset_xml._register_ssm_media(
            BytesIO('1'),
            'image.jpg',
            'img',
            self.generate_metadata('image.jpg', asset_xml)
        )
        mocked_ssmhandler_remove.assert_not_called()
        mocked_ssmhandler_register.assert_not_called()
        mocked_ssmhandler_get_urls.assert_not_called()
        self.assertEqual(u'http://ssm.scielo.org/media/assets/4853/t8krr12',
                         result)

    @patch.object(SSMHandler, 'exists')
    @patch.object(SSMHandler, 'remove')
    @patch.object(SSMHandler, 'register')
    @patch.object(SSMHandler, 'get_urls')
    def test_register_ssm_media_change_asset_if_ssm_asset_exists_and_not_equal(
        self,
        mocked_ssmhandler_get_urls,
        mocked_ssmhandler_register,
        mocked_ssmhandler_remove,
        mocked_ssmhandler_exists
    ):
        mocked_ssmhandler_exists.return_value = (2, [{'uuid': '1234-1234'}])
        mocked_ssmhandler_get_urls.return_value = {
            'url': u'http://ssm.scielo.org/media/assets/4853/filename_t8krr12',
            'url_path': u'/media/assets/4853/filename_t8krr12'
        }
        asset_xml = AssetXML(self.mocked_xylose_article)
        result = asset_xml._register_ssm_media(
            BytesIO('1'),
            'image.jpg',
            'img',
            self.generate_metadata('image.jpg', asset_xml)
        )
        mocked_ssmhandler_remove.assert_called_once_with('1234-1234')
        mocked_ssmhandler_register.assert_called_once()
        self.assertEqual(u'/media/assets/4853/filename_t8krr12', result)

    @patch('opac_proc.core.assets.SSMHandler')
    def test_register_ssm_asset_error_if_sss_handler_exception(
        self,
        MockedSSMHandler
    ):
        MockedSSMHandler.side_effect = Exception()
        asset_xml = AssetXML(self.mocked_xylose_article)
        with self.assertRaises(Exception):
            asset_xml._register_ssm_asset()

    @patch('opac_proc.core.assets.SSMHandler')
    def test_register_ssm_asset_new_sss_handler(
        self,
        MockedSSMHandler
    ):
        instance = MockedSSMHandler.return_value
        instance.exists.return_value = (0, [])
        asset_xml = AssetXML(self.mocked_xylose_article)
        pfile = BytesIO('1')
        asset_xml._register_ssm_asset(
            pfile,
            'article.xml',
            'xml',
            asset_xml.get_metadata()
        )
        MockedSSMHandler.assert_called_once_with(
            pfile,
            'article.xml',
            'xml',
            asset_xml.get_metadata(),
            asset_xml.bucket_name
        )

    @patch.object(SSMHandler, 'exists')
    def test_register_ssm_asset_error_if_handler_method_exception(
        self,
        mocked_ssmhandler_exists
    ):
        mocked_ssmhandler_exists.side_effect = Exception()
        asset_xml = AssetXML(self.mocked_xylose_article)
        with self.assertRaises(Exception):
            asset_xml._register_ssm_asset()

    @patch.object(SSMHandler, 'exists')
    @patch.object(SSMHandler, 'remove')
    @patch.object(SSMHandler, 'register')
    @patch.object(SSMHandler, 'get_urls')
    def test_register_ssm_asset_register_if_ssm_asset_doesnt_exist(
        self,
        mocked_ssmhandler_get_urls,
        mocked_ssmhandler_register,
        mocked_ssmhandler_remove,
        mocked_ssmhandler_exists
    ):
        mocked_ssmhandler_exists.return_value = (0, [])
        mocked_ssmhandler_register.return_value = u'1234-1234'
        mocked_ssmhandler_get_urls.return_value = {
            'url': u'http://ssm.scielo.org/media/assets/4853/article.xml',
            'url_path': u'/media/assets/4853/article.xml'
        }
        asset_xml = AssetXML(self.mocked_xylose_article)
        result = asset_xml._register_ssm_asset(
            BytesIO('1'),
            'article.xml',
            'xml',
            asset_xml.get_metadata()
        )
        mocked_ssmhandler_remove.assert_not_called()
        self.assertEqual(
            (u'1234-1234', u'/media/assets/4853/article.xml'), result)

    @patch.object(SSMHandler, 'exists')
    @patch.object(SSMHandler, 'remove')
    @patch.object(SSMHandler, 'register')
    @patch.object(SSMHandler, 'get_urls')
    def test_register_ssm_asset_returns_existing_ssm_asset_url(
        self,
        mocked_ssmhandler_get_urls,
        mocked_ssmhandler_register,
        mocked_ssmhandler_remove,
        mocked_ssmhandler_exists
    ):
        mocked_ssmhandler_exists.return_value = (
            1,
            [{
                'uuid': '1234-1234',
                'url': u'http://ssm.scielo.org/media/assets/4853/article.xml',
                'full_absolute_url': u'http://ssm.scielo.org/media/assets/4853/article.xml'
            }])
        asset_xml = AssetXML(self.mocked_xylose_article)
        result = asset_xml._register_ssm_asset(
            BytesIO('1'),
            'article.xml',
            'xml',
            asset_xml.get_metadata()
        )
        mocked_ssmhandler_remove.assert_not_called()
        mocked_ssmhandler_register.assert_not_called()
        mocked_ssmhandler_get_urls.assert_not_called()
        self.assertEqual(
            ('1234-1234', u'http://ssm.scielo.org/media/assets/4853/article.xml'),
            result)

    @patch.object(SSMHandler, 'exists')
    @patch.object(SSMHandler, 'remove')
    @patch.object(SSMHandler, 'register')
    @patch.object(SSMHandler, 'get_urls')
    def test_register_ssm_asset_change_asset_if_ssm_asset_exists_and_not_equal(
        self,
        mocked_ssmhandler_get_urls,
        mocked_ssmhandler_register,
        mocked_ssmhandler_remove,
        mocked_ssmhandler_exists
    ):
        mocked_ssmhandler_exists.return_value = (2, [{'uuid': '1234-1234'}])
        mocked_ssmhandler_register.return_value = u'1234-1234'
        mocked_ssmhandler_get_urls.return_value = {
            'url': u'http://ssm.scielo.org/media/assets/4853/article.xml',
            'url_path': u'/media/assets/4853/article.xml'
        }
        asset_xml = AssetXML(self.mocked_xylose_article)
        result = asset_xml._register_ssm_asset(
            BytesIO('1'),
            'article.xml',
            'xml',
            asset_xml.get_metadata()
        )
        mocked_ssmhandler_remove.assert_called_once_with('1234-1234')
        self.assertEqual(
            ('1234-1234', u'/media/assets/4853/article.xml'), result)

    def test_register_xml_medias_no_medias(self):
        def no_medias():
            return
            yield

        asset_xml = AssetXML(self.mocked_xylose_article)
        with patch.object(AssetXML, '_get_content'):
            with patch.object(AssetXML, '_get_media') as \
                    mocked_extract_media:
                mocked_extract_media.side_effect = no_medias
                asset_xml._register_xml_medias()

    @patch.object(AssetXML, '_get_content')
    @patch.object(AssetXML, '_open_asset')
    @patch.object(AssetXML, '_register_ssm_media')
    def test_register_xml_medias_error_if_ssm_handler_error(
        self,
        mocked_get_create_ssm_media,
        mocked_open_asset,
        mocked_get_content
    ):
        self.setup_register_xml_medias_tests()
        mocked_open_asset.side_effect = self.medias_bytes
        mocked_get_content.return_value = self.xml_content
        mocked_get_create_ssm_media.side_effect = Exception()
        asset_xml = AssetXML(self.mocked_xylose_article)
        with self.assertRaises(Exception):
            asset_xml._register_xml_medias()

    @patch.object(AssetXML, '_get_content')
    @patch.object(AssetXML, '_open_asset')
    @patch.object(AssetXML, '_register_ssm_media')
    def test_register_xml_medias_register_all_ssm_assets(
        self,
        mocked_get_create_ssm_media,
        mocked_open_asset,
        mocked_get_content
    ):
        self.setup_register_xml_medias_tests()
        mocked_open_asset.side_effect = self.medias_bytes
        mocked_get_content.return_value = self.xml_content
        mocked_get_create_ssm_media.side_effect = [
            'data/' + filename
            for filename in self.filenames
        ]
        asset_xml = AssetXML(self.mocked_xylose_article)
        medias_args = [
            call(media,
                 filename,
                 "img",
                 self.generate_metadata(filename, asset_xml))
            for media, filename in zip(self.medias_bytes, self.filenames)
        ]
        asset_xml._register_xml_medias()
        self.assertEqual(
            mocked_get_create_ssm_media.mock_calls,
            medias_args
        )

    @patch.object(AssetXML, '_get_content')
    @patch.object(AssetXML, '_open_asset')
    @patch.object(AssetXML, '_register_ssm_media')
    def test_register_xml_medias_changes_content(
        self,
        mocked_get_create_ssm_media,
        mocked_open_asset,
        mocked_get_content
    ):
        self.setup_register_xml_medias_tests()
        mocked_open_asset.side_effect = self.medias_bytes
        mocked_get_content.return_value = self.xml_content
        mocked_get_create_ssm_media.side_effect = [
            'data/' + filename
            for filename in self.filenames
        ]
        expected_xml = """<?xml version="1.0" encoding="utf-8"?>
        <article xmlns:xlink="http://www.w3.org/1999/xlink">
            <body>
                <graphic mimetype="image" xlink:href="data/1414-431X-bjmbr-1414-431X20176177-gf01.jpg"/>
            	<graphic mimetype="image" xlink:href="data/1414-431X-bjmbr-1414-431X20176177-gf02.jpg"/>
            	<graphic mimetype="image" xlink:href="data/1414-431X-bjmbr-1414-431X20176177-gf03.jpg"/>
            	<graphic mimetype="image" xlink:href="data/1414-431X-bjmbr-1414-431X20176177-gf04.jpg"/>
            	<graphic mimetype="image" xlink:href="data/1414-431X-bjmbr-1414-431X20176177-gf05.jpg"/>
            	<graphic mimetype="image" xlink:href="data/1414-431X-bjmbr-1414-431X20176177-gf06.jpg"/>
            	<graphic mimetype="image" xlink:href="data/1414-431X-bjmbr-1414-431X20176177-gf07.jpg"/>
            </body>
        </article>"""
        expected = etree.fromstring(expected_xml,
                                    etree.XMLParser(remove_blank_text=True))
        asset_xml = AssetXML(self.mocked_xylose_article)
        asset_xml._register_xml_medias()
        self.assertEqual(
            etree.tostring(expected.getroottree(), xml_declaration=True, encoding='utf-8'),
            etree.tostring(asset_xml._content.getroottree(), xml_declaration=True, encoding='utf-8')
        )

    @patch('opac_proc.core.assets.HTMLGenerator.parse')
    @patch.object(AssetXML, '_get_content')
    def test_register_htmls_calls_packtools_html_generator_parse(
        self,
        mocked_get_content,
        mocked_html_generator_parse
    ):
        mocked_get_content.return_value = self.xml_content
        asset_xml = AssetXML(self.mocked_xylose_article)
        asset_xml.register_htmls()
        mocked_html_generator_parse.assert_called_once_with(
            self.xml_content,
            valid_only=False,
            css=config.OPAC_PROC_ARTICLE_CSS_URL,
            print_css=config.OPAC_PROC_ARTICLE_PRINT_CSS_URL,
            js=config.OPAC_PROC_ARTICLE_JS_URL
        )

    @patch('opac_proc.core.assets.HTMLGenerator.parse')
    @patch('opac_proc.core.assets.logger.error')
    @patch.object(AssetXML, '_get_content')
    def test_register_htmls_log_error_if_packtools_html_generator_error(
        self,
        mocked_get_content,
        mocked_logger_error,
        mocked_html_generator_parse
    ):
        mocked_get_content.return_value = self.xml_content
        mocked_html_generator_parse.side_effect = ValueError('invalid XML')
        asset_xml = AssetXML(self.mocked_xylose_article)
        asset_xml.register_htmls()
        mocked_logger_error.assert_called_once_with(
            'Error getting htmlgenerator: invalid XML.')

    @patch('opac_proc.core.assets.etree.tostring')
    @patch('opac_proc.core.assets.logger.error')
    @patch.object(AssetXML, '_get_path')
    def test_register_htmls_error_if_etree_tostring_error(
        self,
        mocked_get_path,
        mocked_logger_error,
        mocked_etree_tostring
    ):
        mocked_get_path.return_value = self._article_xml
        mocked_etree_tostring.side_effect = Exception()
        # Article in 'es' translated to 'en'
        article_json = json.loads(self._article_json)
        document = Article(article_json)
        asset_xml = AssetXML(document)
        asset_xml.register_htmls()
        logger_calls = [
            call('Error converting etree {} to string. '.format(lang))
            for lang in ('es', 'en')
        ]
        self.assertEqual(
            mocked_logger_error.mock_calls,
            logger_calls
        )

    @patch('opac_proc.core.assets.logger.error')
    @patch.object(AssetXML, '_get_path')
    @patch.object(AssetXML, '_register_ssm_asset')
    def test_register_htmls_error_if_register_ssm_error(
        self,
        mocked_register_ssm_asset,
        mocked_get_path,
        mocked_logger_error
    ):
        mocked_get_path.return_value = self._article_xml
        mocked_register_ssm_asset.side_effect = Exception()
        # Article in 'es' translated to 'en'
        article_json = json.loads(self._article_json)
        document = Article(article_json)
        asset_xml = AssetXML(document)
        with self.assertRaises(Exception):
            asset_xml.register_htmls()

    @patch('opac_proc.core.assets.SSMHandler', new=SSMHandlerStub)
    @patch.object(AssetXML, '_get_path')
    def test_register_htmls_generates_translated_htmls(self, mocked_get_path):
        # Article in 'es' translated to 'en'
        mocked_get_path.return_value = self._article_xml
        article_json = json.loads(self._article_json)
        document = Article(article_json)
        asset_xml = AssetXML(document)
        generated_htmls = asset_xml.register_htmls()
        self.assertEqual(len(generated_htmls), 2)
        self.assertEqual(generated_htmls[0]['type'], 'html')
        self.assertEqual(generated_htmls[0]['lang'], 'es')
        self.assertEqual(generated_htmls[1]['type'], 'html')
        self.assertEqual(generated_htmls[1]['lang'], 'en')

    @skip("LOCAL TEST ONLY")
    @patch('opac_proc.core.assets.SSMHandler', new=SSMHandlerStub)
    @patch.object(AssetXML, '_get_path')
    def test_register_success(self, mocked_get_path):
        mocked_get_path.return_value = self._article_xml
        article_json = json.loads(self._article_json)
        document = Article(article_json)
        asset_xml = AssetXML(document)
        uuid, xml_url = asset_xml.register()
        self.assertIsNotNone(uuid)
        self.assertIsNotNone(xml_url)
        self.assertEqual(uuid, '123456789-123456789')
        generated_htmls = asset_xml.register_htmls()
        self.assertEqual(generated_htmls[0]['type'], 'html')
        self.assertEqual(generated_htmls[0]['lang'], 'es')
        self.assertEqual(generated_htmls[1]['type'], 'html')
        self.assertEqual(generated_htmls[1]['lang'], 'en')
