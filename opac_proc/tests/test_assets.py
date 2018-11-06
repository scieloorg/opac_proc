# coding: utf-8
import inspect
import json
import os
from datetime import datetime
from io import BytesIO
from unittest import skip
from urlparse import urlsplit

from bs4 import BeautifulSoup
from lxml import etree
from mock import patch, call
from xylose.scielodocument import Article

from base import BaseTestCase
from opac_proc.core import utils
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


HTML_TEST_CONTENT = """<!--version=html-->
<body>
    <p align="center">
        <img src="http:/img/fbpe/test/v1n2/01fig01.jpg">
    </p>
    <p align="center">
        <a href="/img/revistas/test/v1n2/01fig04.png">
    </p>
    <p align="center">
        <img src="img/revistas/test/v1n2/01fig05.png">
    </p>
    <p align="center">
        <embed src="videos/test/v1n2/01fig10.avi">
    </p>
    <p align="center"><strong>Legenda Teste</strong></p>
</body>
"""


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


class MockedXyloseArticleHTML:
    def __init__(self):
        self.collection_acronym = u'scl'
        self.journal = MockedXyloseJournal()
        self.assets_code = u'v1n2'
        self.data_model_version = 'html'
        self.doi = u'10.2564/0101-01012018000100001'
        self.publisher_id = u'S0101-01012018000100001'

    def original_language(self, iso_format=None):
        return u'es'

    def original_html(self, iso_format=None):
        return HTML_TEST_CONTENT

    def translated_htmls(self, iso_format=None):
        return {
            u'pt': '{}\n<p>Portugues</p>'.format(HTML_TEST_CONTENT),
            u'en': '{}\n<p>English</p>'.format(HTML_TEST_CONTENT),
        }

    def file_code(self, *kwargs):
        return u'html_file'


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
            "1414-431X-bjmbr-1414-431X20176177-gf04",
            "1414-431X-bjmbr-1414-431X20176177-gf06.avi",
        ]
        medias = [
            element.attrib[attrib_key]
            for element, attrib_key in asset._get_media()
        ]
        self.assertEqual(len(medias), 5)
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
            ("graphic.tiff", "graphic.jpg"),
            ("image.gif", "image.gif"),
            ("table", "table.jpg"),
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

    @patch.object(AssetXML, '_get_path')
    @patch.object(AssetXML, '_get_content')
    def test_register_returns_none_if_no_content(
        self,
        mocked_get_content,
        mocked_get_path
    ):
        mocked_get_content.return_value = None
        asset_xml = AssetXML(self.mocked_xylose_article)
        xml_url = asset_xml.register()
        self.assertIsNone(xml_url)

    @skip("LOCAL TEST ONLY")
    @patch('opac_proc.core.assets.SSMHandler', new=SSMHandlerStub)
    @patch.object(AssetXML, '_get_path')
    def test_register_success(self, mocked_get_path):
        mocked_get_path.return_value = self._article_xml
        article_json = json.loads(self._article_json)
        document = Article(article_json)
        asset_xml = AssetXML(document)
        xml_url = asset_xml.register()
        self.assertIsNotNone(xml_url)
        generated_htmls = asset_xml.register_htmls()
        self.assertEqual(generated_htmls[0]['type'], 'html')
        self.assertEqual(generated_htmls[0]['lang'], 'es')
        self.assertEqual(generated_htmls[1]['type'], 'html')
        self.assertEqual(generated_htmls[1]['lang'], 'en')


class TestAssetHTMLS(BaseTestCase):

    def setUp(self):
        self.mocked_xylose_article = MockedXyloseArticleHTML()
        self.htmls = {
            self.mocked_xylose_article.original_language():
                self.mocked_xylose_article.original_html()
        }
        self.htmls.update(self.mocked_xylose_article.translated_htmls())
        self.template_directory = os.path.join(
            os.path.dirname(inspect.getmodule(AssetHTMLS).__file__),
            'templates'
        )
        ssm_in_memory.clear()

    def test_AssetHTMLS2(self):
        asset_xml = AssetHTMLS(self.mocked_xylose_article)
        self.assertEqual(
            asset_xml.xylose,
            self.mocked_xylose_article)
        self.assertIsNone(asset_xml._content)

    @patch.object(AssetHTMLS, '_add_htmls')
    def test_register_must_call_add_htmls(
        self,
        mocked_add_htmls
    ):
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        asset_htmls.register()
        mocked_add_htmls.assert_called_once_with(self.htmls)

    @patch.object(AssetHTMLS, '_add_htmls')
    @patch.object(MockedXyloseArticleHTML, 'original_html')
    def test_register_no_article_original_html(
        self,
        mocked_original_html,
        mocked_add_htmls
    ):
        mocked_original_html.return_value = None
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        asset_htmls.register()
        mocked_add_htmls.assert_called_once_with(
            self.mocked_xylose_article.translated_htmls())

    @patch.object(AssetHTMLS, '_add_htmls')
    @patch('opac_proc.core.assets.logger.error')
    @patch.object(MockedXyloseArticleHTML, 'original_html')
    @patch.object(MockedXyloseArticleHTML, 'translated_htmls')
    def test_register_no_htmls(
        self,
        mocked_translated_htmls,
        mocked_original_html,
        mocked_logger_error,
        mocked_add_htmls
    ):
        mocked_original_html.return_value = None
        mocked_translated_htmls.return_value = None
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        asset_htmls.register()
        mocked_logger_error.assert_called_once_with(
            u"Artigo com o PID: %s, não tem HTML",
            self.mocked_xylose_article.publisher_id
        )
        mocked_add_htmls.assert_not_called()

    @patch.object(AssetHTMLS, '_add_htmls')
    def test_register_must_returns_add_htmls_result(
        self,
        mocked_add_htmls
    ):
        expected = {
            'type': 'html',
            'lang': 'en',
            'url': 'https://teste.scielo.br/media/assets/test/v1n1/01.html'
        }
        mocked_add_htmls.return_value = expected
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        result = asset_htmls.register()
        self.assertIsNotNone(result)
        self.assertEqual(result, expected)

    @patch('opac_proc.core.assets.BeautifulSoup')
    @patch.object(AssetHTMLS, '_register_html_media_assets')
    @patch.object(AssetHTMLS, '_register_ssm_asset')
    def test_add_htmls_must_create_soup_objects(
        self,
        mocked_register_ssm_asset,
        mocked_register_html_media_assets,
        MockedBeautifulSoup
    ):
        mocked_register_ssm_asset.return_value = (
            None,
            '/aaj/v1n1/{}.html'.format(self.mocked_xylose_article.file_code())
        )
        expected = [
            call(html, 'html.parser')
            for html in self.htmls.values()
        ]
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        asset_htmls._add_htmls(self.htmls)
        MockedBeautifulSoup.assert_has_calls(expected, any_order=True)

    @patch('opac_proc.core.assets.BeautifulSoup')
    @patch.object(AssetHTMLS, '_register_html_media_assets')
    @patch.object(AssetHTMLS, '_register_ssm_asset')
    def test_add_htmls_must_call_register_html_media_assets_with_parsed_html(
        self,
        mocked_register_ssm_asset,
        mocked_register_html_media_assets,
        MockedBeautifulSoup
    ):
        parsed_htmls = [
            BeautifulSoup(html, 'html.parser')
            for html in self.htmls.values()
        ]
        MockedBeautifulSoup.side_effect = parsed_htmls
        mocked_register_ssm_asset.return_value = (
            None,
            '/aaj/v1n1/{}.html'.format(self.mocked_xylose_article.file_code())
        )
        expected = [
            call(parsed_html)
            for parsed_html in parsed_htmls
        ]
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        asset_htmls._add_htmls(self.htmls)
        mocked_register_html_media_assets.assert_has_calls(
            expected, any_order=True)

    @patch('opac_proc.core.assets.SSMHandler', new=SSMHandlerStub)
    @patch('opac_proc.core.assets.utils.render_from_template')
    @patch.object(AssetHTMLS, '_register_html_media_assets')
    def test_add_htmls_must_call_utils_render_from_template_with_updated_html(
        self,
        mocked_register_html_media_assets,
        mocked_render_from_template
    ):
        mocked_register_html_media_assets.side_effect = self.htmls.values()
        mocked_render_from_template.side_effect = self.htmls.values()
        expected = [
            call(
                self.template_directory,
                'article.html',
                {
                    'html': html,
                    'css': config.OPAC_PROC_ARTICLE_CSS_URL,
                    'css_print': config.OPAC_PROC_ARTICLE_PRINT_CSS_URL
                }
            )
            for html in self.htmls.values()
        ]
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        asset_htmls._add_htmls(self.htmls)
        self.assertEqual(mocked_render_from_template.mock_calls, expected)

    @patch.object(AssetHTMLS, '_register_ssm_asset')
    def test_add_htmls_must_call_register_ssm_asset_for_each_html(
        self,
        mocked_register_ssm_asset
    ):
        mocked_register_ssm_asset.side_effect = [(1, ''), (2, ''), (3, '')]
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        asset_htmls._add_htmls(self.htmls)
        self.assertEqual(
            len(mocked_register_ssm_asset.mock_calls), len(self.htmls))

    @patch.object(AssetHTMLS, '_register_ssm_asset')
    def test_add_htmls_returns_registered_htmls(
        self,
        mocked_register_ssm_asset
    ):
        test_urls = [
            ('uuid' + lang,
             'http://ssm.scielo.br/assets/test/v1n2/{}.html'.format(lang))
            for lang in self.htmls.keys()
        ]
        expected = [
            {
                'type': 'html',
                'lang': lang,
                'url': html_url
            }
            for lang, html_url in zip(self.htmls.keys(),
                                      [x[1] for x in test_urls])
        ]
        mocked_register_ssm_asset.side_effect = test_urls
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        result = asset_htmls._add_htmls(self.htmls)
        self.assertIsNotNone(result)
        self.assertEqual(result, expected)

    @patch('opac_proc.core.assets.SSMHandler', new=SSMHandlerStub)
    @patch.object(AssetHTMLS, '_open_asset')
    @patch.object(AssetHTMLS, '_normalize_media_path')
    def test_register_html_media_assets_must_call_normalize_media_path(
        self,
        mocked_normalize_media_path,
        mocked_open_asset
    ):
        html_test_content = """<!--version=html-->
        <p>&nbsp;</p>
        <p align="center">
            <img src="img/revistas/test/v1n2/01fig05.png"></p>
        <p>&nbsp;</p>
        <p align="center"><strong>Legenda Teste</strong></p>
        """
        mocked_open_asset.return_value = BytesIO(b'12345')
        parsed_html = BeautifulSoup(html_test_content, 'html.parser')
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        expected = "img/revistas/test/v1n2/01fig05.png"
        asset_htmls._register_html_media_assets(parsed_html)
        mocked_normalize_media_path.assert_called_once_with(expected)

    @patch('opac_proc.core.assets.SSMHandler', new=SSMHandlerStub)
    @patch.object(AssetHTMLS, '_open_asset')
    @patch.object(AssetHTMLS, '_normalize_media_path')
    def test_register_html_media_assets_must_no_normalize_media_path_call_if_invalid_file(
        self,
        mocked_normalize_media_path,
        mocked_open_asset
    ):
        html_test_content = """<!--version=html-->
        <p>&nbsp;</p>
        <p align="center">
            <embed src="img/revistas/test/v1n2/01fig08.3gp"></p>
        <p>&nbsp;</p>
        <p align="center"><strong>Legenda Teste</strong></p>
        """
        mocked_open_asset.return_value = BytesIO(b'12345')
        parsed_html = BeautifulSoup(html_test_content, 'html.parser')
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        asset_htmls._register_html_media_assets(parsed_html)
        mocked_normalize_media_path.assert_not_called()

    @patch('opac_proc.core.assets.SSMHandler', new=SSMHandlerStub)
    @patch.object(AssetHTMLS, '_register_ssm_media')
    @patch.object(AssetHTMLS, '_open_asset')
    def test_register_html_media_assets_must_open_asset_with_media_path(
        self,
        mocked_open_asset,
        mocked_register_ssm_media
    ):
        html_test_content = """<!--version=html-->
        <p>&nbsp;</p>
        <p align="center">
            <img src="img/revistas/test/v1n2/01fig05.png"></p>
        <p>&nbsp;</p>
        <p align="center"><strong>Legenda Teste</strong></p>
        """
        parsed_html = BeautifulSoup(html_test_content, 'html.parser')
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        expected = asset_htmls._normalize_media_path(
            "img/revistas/test/v1n2/01fig05.png")
        asset_htmls._register_html_media_assets(parsed_html)
        mocked_open_asset.assert_called_once_with(expected)

    @patch.object(AssetHTMLS, '_open_asset')
    @patch.object(AssetHTMLS, '_register_ssm_media')
    def test_register_html_media_assets_no_register_ssm_media_if_open_asset_error(
        self,
        mocked_register_ssm_media,
        mocked_open_asset
    ):
        parsed_html = BeautifulSoup(HTML_TEST_CONTENT, 'html.parser')
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        mocked_open_asset.side_effect = Exception()
        with self.assertRaises(Exception):
            asset_htmls._register_html_media_assets(parsed_html)
            mocked_register_ssm_media.assert_not_called()

    @patch.object(AssetHTMLS, '_open_asset')
    @patch.object(AssetHTMLS, '_register_ssm_media')
    def test_register_html_media_assets_no_register_ssm_media_if_open_asset_none(
        self,
        mocked_register_ssm_media,
        mocked_open_asset
    ):
        parsed_html = BeautifulSoup(HTML_TEST_CONTENT, 'html.parser')
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        mocked_open_asset.return_value = None
        asset_htmls._register_html_media_assets(parsed_html)
        mocked_register_ssm_media.assert_not_called()

    @patch.object(AssetHTMLS, '_open_asset')
    @patch.object(AssetHTMLS, '_register_ssm_media')
    def test_register_html_media_assets_register_ssm_media_if_open_asset_ok(
        self,
        mocked_register_ssm_media,
        mocked_open_asset
    ):
        pfile = BytesIO(b'12345')
        mocked_open_asset.return_value = pfile
        html_test_content = """<!--version=html-->
        <p>&nbsp;</p>
        <p align="center">
            <img src="img/revistas/test/v1n2/01fig05.png"></p>
        <p>&nbsp;</p>
        <p align="center"><strong>Legenda Teste</strong></p>
        """
        parsed_html = BeautifulSoup(html_test_content, 'html.parser')
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        metadata = asset_htmls.get_metadata()
        metadata.update({'file_path': u"/app/data/img/test/v1n2/01fig05.png",
                         'bucket_name': asset_htmls.bucket_name,
                         'type': "img",
                         'origin_path': u"img/revistas/test/v1n2/01fig05.png"})
        asset_htmls._register_html_media_assets(parsed_html)
        mocked_register_ssm_media.assert_called_once_with(
            pfile, u"01fig05.png", "img", metadata)

    def test_normalize_media_path_tif_to_jpg(self):
        asset = AssetHTMLS(self.mocked_xylose_article)
        media_path = 'img/revistas/gs/v29n4/asset.tif'
        expected = '%s/gs/v29n4/asset.jpg' % (
            config.OPAC_PROC_ASSETS_SOURCE_MEDIA_PATH
        )
        new_media_path = asset._normalize_media_path(media_path)
        self.assertIsNotNone(new_media_path)
        self.assertEqual(new_media_path, expected)
        new_media_path = asset._normalize_media_path('/' + media_path)
        self.assertIsNotNone(new_media_path)
        self.assertEqual(new_media_path, expected)

    def test_normalize_media_path_replace_to_source_media_path(self):
        asset = AssetHTMLS(self.mocked_xylose_article)
        media_path = 'img/fbpe/gs/v29n4/asset.gif'
        expected = '%s/gs/v29n4/asset.gif' % (
            config.OPAC_PROC_ASSETS_SOURCE_MEDIA_PATH
        )
        new_media_path = asset._normalize_media_path(media_path)
        self.assertIsNotNone(new_media_path)
        self.assertEqual(new_media_path, expected)
        new_media_path = asset._normalize_media_path('/' + media_path)
        self.assertIsNotNone(new_media_path)
        self.assertEqual(new_media_path, expected)

    @patch('opac_proc.core.assets.SSMHandler', new=SSMHandlerStub)
    @patch.object(AssetHTMLS, '_normalize_media_path')
    @patch.object(AssetHTMLS, '_open_asset')
    def test_register_html_media_assets_calls_normalize_media_path(
        self,
        mocked_open_asset,
        mocked_normalize_media_path
    ):
        file_test = BytesIO(b'12345')
        mocked_open_asset.return_value = file_test
        html_test_content = """<!--version=html-->
        <p>&nbsp;</p>
        <p align="center">
            <a href="/img/fbpe/test/v1n2/html/01tab01.htm">Tabela 1</a></p>
        <p>&nbsp;</p>
        <p align="center"><strong>Legenda Teste</strong></p>
        """
        parsed_html = BeautifulSoup(html_test_content, 'html.parser')
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        expected = "/img/fbpe/test/v1n2/html/01tab01.htm"
        asset_htmls._register_html_media_assets(parsed_html)
        mocked_normalize_media_path.assert_called_once_with(expected)

    @patch('opac_proc.core.assets.SSMHandler', new=SSMHandlerStub)
    @patch('opac_proc.core.assets.BeautifulSoup')
    @patch.object(AssetHTMLS, '_open_asset')
    def test_register_html_media_assets_creates_bsoup_if_html_media_asset(
        self,
        mocked_open_asset,
        MockedBeautifulSoup
    ):
        file_test = BytesIO(b'12345')
        mocked_open_asset.return_value = file_test
        MockedBeautifulSoup.return_value = BeautifulSoup(
            '<body><p>Tests</p></body>')
        html_test_content = """<!--version=html-->
        <p>&nbsp;</p>
        <p align="center">
            <a href="/img/fbpe/test/v1n2/html/01tab01.htm">Tabela 1</a></p>
        <p>&nbsp;</p>
        <p align="center"><strong>Legenda Teste</strong></p>
        """
        parsed_html = BeautifulSoup(html_test_content, 'html.parser')
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        asset_htmls._register_html_media_assets(parsed_html)
        MockedBeautifulSoup.assert_called_once()

    @patch('opac_proc.core.assets.BeautifulSoup')
    @patch.object(AssetHTMLS, '_open_asset')
    def test_register_html_media_assets_no_bsoup_if_open_asset_error(
        self,
        mocked_open_asset,
        MockedBeautifulSoup
    ):
        mocked_open_asset.return_value = None
        html_test_content = """<!--version=html-->
        <p>&nbsp;</p>
        <p align="center">
            <a href="/img/fbpe/test/v1n2/html/01tab01.htm">Tabela 1</a></p>
        <p>&nbsp;</p>
        <p align="center"><strong>Legenda Teste</strong></p>
        """
        parsed_html = BeautifulSoup(html_test_content, 'html.parser')
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        asset_htmls._register_html_media_assets(parsed_html)
        MockedBeautifulSoup.assert_not_called()

    @patch.object(AssetHTMLS, '_open_asset')
    @patch.object(AssetHTMLS, '_register_ssm_media')
    def test_register_html_media_assets_calls_register_ssm_media(
        self,
        mocked_register_ssm_media,
        mocked_open_asset
    ):
        pfile = BytesIO(b'01tab01.htm')
        mocked_open_asset.return_value = pfile
        html_test_content = """<!--version=html-->
        <p>&nbsp;</p>
        <p align="center">
            <a href="/img/fbpe/test/v1n2/html/01tab01.htm">Tabela 1</a></p>
        <p>&nbsp;</p>
        <p align="center"><strong>Legenda Teste</strong></p>
        """
        parsed_html = BeautifulSoup(html_test_content, 'html.parser')
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        metadata = asset_htmls.get_metadata()
        metadata.update({
            'file_path': u"/app/data/img/test/v1n2/html/01tab01.htm",
            'bucket_name': asset_htmls.bucket_name,
            'type': "img",
            'origin_path': u"/img/fbpe/test/v1n2/html/01tab01.htm"})
        asset_htmls._register_html_media_assets(parsed_html)
        mocked_register_ssm_media.assert_called_once()

    @patch('opac_proc.core.assets.SSMHandler', new=SSMHandlerStub)
    @patch.object(AssetHTMLS, '_open_asset')
    def test_register_html_media_assets_returns_updated_html(
        self,
        mocked_open_asset
    ):
        HTML_EXTRAS = [
            ('img', "/img/fbpe/test/v1n2/01fig02.gif"),
            ('img', "img/fbpe/test/v1n2/01fig03.mp4"),
            ('img', "img/revistas/test/v1n2/01fig06.tif"),
            ('img', "img/revistas/test/v1n2/01fig07.tiff"),
            ('img', "https://www.revista.com/img/revistas/test/v1n2/01fig07.jpg"),
            ('embed', "img/revistas/test/v1n2/01fig08.3gp"),
            ('embed', "img/revistas/test/v1n2/01fig09.avi"),
        ]
        parsed_html = BeautifulSoup(HTML_TEST_CONTENT, 'html.parser')
        for attr, url in HTML_EXTRAS:
            p_tag = parsed_html.new_tag("p", align="center")
            media_tag = parsed_html.new_tag(attr, src=url)
            p_tag.append(media_tag)
            parsed_html.body.append(p_tag)
        p_tag = parsed_html.new_tag("p", align="center")
        media_tag = parsed_html.new_tag(
            "a", href="/img/fbpe/test/v1n2/html/01tab01.htm")
        media_tag.string = "Tabela 1"
        p_tag.append(media_tag)
        parsed_html.body.append(p_tag)
        asset_htmls = AssetHTMLS(self.mocked_xylose_article)
        tags = [
            ('src', tag)
            for tag in parsed_html.find_all(src=True)
            if asset_htmls._is_valid_media_file(urlsplit(tag['src']))
        ]
        tags = tags + [
            ('href', tag)
            for tag in parsed_html.find_all(href=True)
        ]
        changed_urls = [
            asset_htmls._normalize_media_path(
                'media/assets/test/v1n2/' + os.path.split(tag[attr])[-1]
            )
            for attr, tag in tags
        ]
        tmp_files = [
            BytesIO(changed_url.encode('utf-8'))
            for changed_url in changed_urls
        ]
        mocked_open_asset.side_effect = tmp_files
        result = asset_htmls._register_html_media_assets(parsed_html)
        self.assertIsNotNone(result)
        self.assertNotEqual(result, parsed_html)
        for expected in changed_urls:
            self.assertIn(expected.encode('utf-8'), str(result))
