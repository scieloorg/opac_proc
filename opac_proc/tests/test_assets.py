# coding: utf-8
import json
import urllib2

from bs4 import BeautifulSoup
from xylose.scielodocument import Article

from base import BaseTestCase
from opac_proc.core.assets import Assets


class TestAssets(BaseTestCase):

    def setUp(self):
        self.am_api_url = 'http://articlemeta.scielo.org/api/v1/article/?code={}&format={}'

    def test_article_transform_html_extract_media(self):
        article_json = json.loads(
            urllib2.urlopen(
                self.am_api_url.format('S0001-37652004000400001', 'json')
            ).read()
        )
        document = Article(article_json)
        asset = Assets(document)
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

    def test_article_transform_xml_extract_media(self):
        article_json = json.loads(
            urllib2.urlopen(
                self.am_api_url.format('S0100-879X2017001100602', 'json')
            ).read()
        )
        document = Article(article_json)
        asset = Assets(document)
        asset.content = """<?xml version="1.0" encoding="utf-8"?>
        <article xmlns:xlink="http://www.w3.org/1999/xlink">
            <graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf01.tif"/>
			<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf02.tif"/>
			<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf03.tif"/>
			<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf04.tif"/>
			<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf05.tif"/>
			<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf06.tif"/>
			<graphic mimetype="image" xlink:href="1414-431X-bjmbr-1414-431X20176177-gf07.tif"/>
        </article>"""
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
