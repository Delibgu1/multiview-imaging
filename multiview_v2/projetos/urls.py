from django.urls import path
from .views import home

app_name = "projetos"

urlpatterns = [
    path("", home, name="index"),  # exigido pelo template
    path("home/", home, name="home"),
]