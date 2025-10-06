# web/projetos/urls.py
from django.urls import path
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, RedirectView
from . import views
from .views import (
    ProjetoListView,
    ProjetoCreateView,
    ProjetoUpdateView,
    ProjetoDetailView,
    upload,
    upload_presign,
    gcp_modelo_csv,
)

app_name = "projetos"

def ping(_):
    return HttpResponse("projetos OK", content_type="text/plain")

urlpatterns = [
    path("ping/", ping, name="ping"),

    path("", views.ProjetoListView.as_view(), name="index"),
    path("projetos/", ProjetoListView.as_view(), name="index"),
    path(
        "objetivo/",
        TemplateView.as_view(template_name="projetos/paginas/objetivo.html"),
        name="objetivo",
    ),
    path(
        "configuracoes/",
        RedirectView.as_view(pattern_name="projetos:objetivo", permanent=False),
        name="configuracoes_legacy",
    ),

    path("novo/", views.ProjetoCreateView.as_view(), name="new"),
    path("<int:pk>/upload/", views.upload, name="upload"),
    path("<int:pk>/upload/presign/", views.upload_presign, name="upload_presign"),
    path("gcp-modelo.csv", views.gcp_modelo_csv, name="gcp_modelo_csv"),
    path("<int:pk>/", views.ProjetoDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", views.ProjetoUpdateView.as_view(), name="edit"),
    path(
        "comprar-creditos/",
        views.ComprarCreditosView.as_view(),
        name="comprar_creditos",
    ),
]