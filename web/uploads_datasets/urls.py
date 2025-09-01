
from django.urls import path
from . import views

app_name = "uploads"

urlpatterns = [
    path("", views.upload_page, name="upload_page"),
    path("presign/", views.presign, name="presign"),
    path("complete/", views.complete, name="complete"),
]
