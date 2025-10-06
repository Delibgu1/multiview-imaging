# web/core/tests/test_ui_frozen.py
from django.test import TestCase
from django.urls import reverse

class FrozenLoginUITest(TestCase):
    def test_login_renders(self):
        resp = self.client.get(reverse("login"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Login")  # título
        # Rodapé fixo
        self.assertContains(resp, "Plataforma de Processamento de Imagens Multiview")
        self.assertContains(resp, "v0.1.0")
        self.assertContains(resp, "suporte.multiview@sinergicaagro.com.br")
        # Logo (caminho pode ser o branco ou o fallback)
        self.assertTrue(
            ("Logo-multiview-branco.png" in resp.content.decode("utf-8"))
            or ("logo-multiview.png" in resp.content.decode("utf-8"))
        )

class FrozenProjetosListUITest(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        self.user = get_user_model().objects.create_user(
            username="tester", password="x"
        )

    def test_list_empty_state(self):
        self.client.login(username="tester", password="x")
        resp = self.client.get(reverse("projetos:index"))
        self.assertEqual(resp.status_code, 200)
        # Cabeçalho e textos aprovados
        self.assertContains(resp, "Meus Projetos de Imagens")
        self.assertContains(resp, "Você ainda não tem projetos.")
        self.assertContains(resp, "Criar novo projeto")
