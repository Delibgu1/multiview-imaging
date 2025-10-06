
# D:\Dev\multiview_imaging\web\creditos\urls.py
from django.urls import path
from django.views.generic import TemplateView

app_name = "creditos"

urlpatterns = [
    path("", TemplateView.as_view(template_name="core/placeholder.html"), name="index"),
]