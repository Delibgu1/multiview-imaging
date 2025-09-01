# multiview/multiview_imaging/web/projetos/urls.py (fixed)
from django.urls import path
from django.http import HttpResponse
from . import views


from .views import (
    ProjetoListView,
    ProjetoCreateView,
    ProjetoDetailView,
    ProjetoUpdateView,
)

app_name = "projetos"

def ping(_):
    return HttpResponse("projetos OK", content_type="text/plain")

urlpatterns = [
    path("ping/", ping, name="ping"),
    path("", views.ProjetoListView.as_view(), name="index"),
    path("novo/", views.ProjetoCreateView.as_view(), name="new"),
    path("<int:pk>/", views.ProjetoDetailView.as_view(), name="detail"),
    path("<int:pk>/upload/", views.upload, name="upload"),
    path("<int:pk>/upload/presign/", views.upload_presign, name="upload_presign"),
    path("<int:pk>/upload/associar/", views.upload_associar, name="upload_associar"),
    path("<int:pk>/upload/remover/", views.upload_remover, name="upload_remover"),
    path("gcp-modelo.csv", views.gcp_modelo_csv, name="gcp_modelo_csv"),
]


