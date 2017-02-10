from base import BaseTestCase
from flask import current_app


class TestHomeView(BaseTestCase):

    def test_home_page_without_errors(self):
        """
        Teste simples acessando a home da app e verificando que a
        resposta tem retorno 200 OK e usando o template esperado
        """
        with current_app.app_context():
            response = self.client.get("/")
            self.assert_200(response)
            self.assert_template_used('home.html')
