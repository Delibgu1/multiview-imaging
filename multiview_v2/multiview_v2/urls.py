from django.contrib import admin
from django.urls import path, include
from core.views import principal as core_principal  # alias para {% url 'index' %}

urlpatterns = [
    # alias global: {% url 'index' %}
    path("", core_principal, name="index"),

    # namespaces
    path("admin/", admin.site.urls),
    path("", include("core.urls", namespace="core")),
    path("processamento/", include("processamento.urls", namespace="processamento")),
    path("projetos/", include("projetos.urls", namespace="projetos")),
]