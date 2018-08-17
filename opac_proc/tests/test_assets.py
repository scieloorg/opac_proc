# coding: utf-8
from bs4 import BeautifulSoup

from base import BaseTestCase
from opac_proc.core.assets import Assets
from opac_proc.web import config


class TestAssets(BaseTestCase):

    def setUp(self):
        class MockedXyloseJournal:
            def __init__(self):
                self.acronym = 'test'

        class MockedXyloseArticle:
            def __init__(self):
                self.journal = MockedXyloseJournal()
                self.assets_code = '0001-0203'
                self.data_model_version = 'xml'

        self.mocked_xylose_article = MockedXyloseArticle()

    def test_article_transform_html_extract_media(self):
        self.mocked_xylose_article.data_model_version = 'html'
        asset = Assets(self.mocked_xylose_article)
        asset.content = """
        <!-- <img src="/img/revistas/aabc/v76n4/a01img00.gif " /> -->
        <p align="center"><img src="/img/revistas/aabc/v76n4/a01img26.gif " /></p>
        <p><font size="2" face="verdana"> Here, <img src="/img/revistas/aabc/v76n4/a01img27.gif" align="absmiddle" />,<font face="symbol">    \xbc</font>, <img src="/img/revistas/aabc/v76n4/a01img28.gif" align="absmiddle" />    are the eigenvalues of <i>A</i> = \x96<i>dg</i>, where <i>g</i> : <i>M<sup>n</sup></i>    <font face="symbol">\xae</font> <i>S<sup>n</sup></i>(1) is the Gauss map of the    hypersurface. Reilly showed that orientable hypersurfaces with <i>S<sub>r</sub></i><sub>+1</sub>    = 0 are critical points of the functional </font></p>     <p align="center"><img src="/img/revistas/aabc/v76n4/a01img01.gif " /></p>
        """
        html_soup = BeautifulSoup(asset.content, "html.parser")
        expected = [
            img.get('src').strip().encode('utf-8')
            for img in html_soup.find_all(src=True)
        ]
        medias = asset._extract_media()
        self.assertEqual(len(medias), 4)
        self.assertEqual(medias, expected)

    def test_article_transform_html_extract_media_external_links(self):
        self.mocked_xylose_article.data_model_version = 'html'
        asset = Assets(self.mocked_xylose_article)
        asset.content = """
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

    def test_article_transform_xml_extract_media(self):
        self.mocked_xylose_article.data_model_version = 'xml'
        asset = Assets(self.mocked_xylose_article)
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
        <article xmlns:xlink="http://www.w3.org/1999/xlink">
            <graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf01.tif"/>
			<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf02.tif"/>
			<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf03.tif"/>
			<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf04.tif"/>
			<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf05.tif"/>
			<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf06.tif"/>
			<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf07.tif"/>
        </article>"""
        asset.content = unicode(xml_content)
        expected = [
            "1414-431X-bjmbr-1414-431X20176177-gf01.tif",
            "1414-431X-bjmbr-1414-431X20176177-gf02.tif",
            "1414-431X-bjmbr-1414-431X20176177-gf03.tif",
            "1414-431X-bjmbr-1414-431X20176177-gf04.tif",
            "1414-431X-bjmbr-1414-431X20176177-gf05.tif",
            "1414-431X-bjmbr-1414-431X20176177-gf06.tif",
            "1414-431X-bjmbr-1414-431X20176177-gf07.tif"
        ]
        medias = asset._extract_media()
        self.assertEqual(len(medias), 7)
        self.assertEqual(medias, expected)

    def test_article_transform_xml_extract_media_valid_extensions(self):
        self.mocked_xylose_article.data_model_version = 'xml'
        asset = Assets(self.mocked_xylose_article)
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
        <article xmlns:xlink="http://www.w3.org/1999/xlink">
            <graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf01.tif"/>
			<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf02.jpg"/>
			<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf03.gif"/>
			<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf04.exe"/>
			<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf05.xls"/>
			<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf06.avi"/>
			<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf07.csv"/>
        </article>"""
        asset.content = unicode(xml_content)
        expected = [
            "1414-431X-bjmbr-1414-431X20176177-gf01.tif",
            "1414-431X-bjmbr-1414-431X20176177-gf02.jpg",
            "1414-431X-bjmbr-1414-431X20176177-gf03.gif",
            "1414-431X-bjmbr-1414-431X20176177-gf06.avi",
        ]
        medias = asset._extract_media()
        self.assertEqual(len(medias), 4)
        self.assertEqual(medias, expected)

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
