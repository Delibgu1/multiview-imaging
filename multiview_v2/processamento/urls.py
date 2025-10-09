from django.urls import path
from .views import home

app_name = "processamento"

urlpatterns = [
    path("", home, name="home"),
]