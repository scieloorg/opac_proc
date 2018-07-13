# coding: utf-8
import os

from base import BaseTestCase
from flask import current_app


class TestHomeView(BaseTestCase):

    def test_home_page_redirect_to_login(self):
        """
        Teste simples acessando a home da app e verificando que:
        - a resposta tem retorno 302 (redirect para o /accounts/login)
        - e usando o template esperado
        """
        with current_app.app_context():
            response = self.client.get("/", follow_redirects=False)
            self.assertStatus(response, 302)

    def test_home_page_following_redirect_lands_on_login_page(self):
        """
        Teste simples acessando a home da app e verificando que:
        - a resposta tem retorno 302 (redirect para o /accounts/login)
        - e usando o template esperado
        """
        with current_app.app_context():
            response = self.client.get("/", follow_redirects=True)
            self.assertStatus(response, 200)
            self.assert_template_used('accounts/login.html')


class TestStaticCatalogView(BaseTestCase):

    def setUp(self):
        self.app = self.create_app()
        self.proj_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..')
        )

    def test_download_static_pdf_files_response(self):
        """"""
        static_filename = 'static_pdf_files.txt'
        filename_fullpath = os.path.join(self.proj_path,
                                         'web/static/catalog',
                                         static_filename)
        with open(filename_fullpath, 'w') as fp:
            fp.write('./file_path/file.pdf')

        with self.app.app_context():
            response = self.client.get("/%s" % static_filename,
                                       follow_redirects=True)
            self.assertStatus(response, 200)

    def test_download_static_html_files_response(self):
        """"""
        static_filename = 'static_html_files.txt'
        filename_fullpath = os.path.join(self.proj_path,
                                         'web/static/catalog',
                                         static_filename)
        with open(filename_fullpath, 'w') as fp:
            fp.write('./file_path/file.html')

        with self.app.app_context():
            response = self.client.get("/%s" % static_filename,
                                       follow_redirects=True)
            self.assertStatus(response, 200)

    def test_download_static_xml_files_response(self):
        """"""
        static_filename = 'static_xml_files.txt'
        filename_fullpath = os.path.join(self.proj_path,
                                         'web/static/catalog',
                                         static_filename)
        with open(filename_fullpath, 'w') as fp:
            fp.write('./file_path/file.xml')

        with self.app.app_context():
            response = self.client.get("/%s" % static_filename,
                                       follow_redirects=True)
            self.assertStatus(response, 200)

    def test_download_static_files_not_found(self):
        """"""
        with self.app.app_context():
            response = self.client.get('static_doc_files.txt',
                                       follow_redirects=True)
            self.assertStatus(response, 404)
