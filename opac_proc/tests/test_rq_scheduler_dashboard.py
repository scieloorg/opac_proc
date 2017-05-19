# coding: utf-8
from base import BaseTestCase
from flask import current_app


class TestRQSchedulerDashboardView(BaseTestCase):

    def test_scheduler_dashboard_page_redirect_to_login(self):
        """
        Teste simples acessando a /dashboard/ da app e verificando que:
        - a resposta tem retorno 302 (redirect para o /accounts/login)
        - e usando o template esperado
        """
        with current_app.app_context():
            response = self.client.get("/scheduler/", follow_redirects=False)
            self.assertStatus(response, 302)

    def test_scheduler_dashboard_page_following_redirect_lands_on_login_page(self):
        """
        Teste simples acessando a home da app e verificando que:
        - a resposta tem retorno 302 (redirect para o /accounts/login)
        - e usando o template esperado
        """
        with current_app.app_context():
            response = self.client.get("/scheduler/", follow_redirects=True)
            self.assertStatus(response, 200)
            self.assert_template_used('accounts/login.html')
