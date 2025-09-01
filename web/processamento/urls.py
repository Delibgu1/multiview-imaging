
from django.urls import path
from . import views

app_name = "processamento"

urlpatterns = [
    path("", views.index, name="index"),
]
