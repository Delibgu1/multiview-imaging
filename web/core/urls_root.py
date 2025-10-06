
# web/core/urls_root.py
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import RedirectView
from django.templatetags.static import static as static_url
from . import views

from core import views as core_views

app_name = "core"

urlpatterns = [
    # Raiz: se logado vai pra principal; senão, pro login
    path("", core_views.home_redirect, name="home"),

    # Admin
    path("admin/", admin.site.urls),

    # Ícone (favicon)
    path("favicon.ico", RedirectView.as_view(
        url=static_url("core/img/favicon.ico"), permanent=False
    )),

    # Rotas do app core (namespaced: core)
    path("", include(("core.urls", "core"), namespace="core")),

    # >>> inclusão do app 'projetos' com namespace
    path("projetos/", include(("projetos.urls", "projetos"), namespace="projetos")),


]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
