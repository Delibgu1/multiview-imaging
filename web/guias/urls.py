
# D:\Dev\multiview_imaging\web\guias\urls.py
from django.urls import path
from django.views.generic import TemplateView

app_name = "guias"

urlpatterns = [
    path("", TemplateView.as_view(template_name="core/placeholder.html"), name="index"),
]
