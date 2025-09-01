# multiview/multiview_imaging/web/core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Auth (templates em core/templates/registration/)
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),

    # App
    path("", RedirectView.as_view(pattern_name="projetos:index", permanent=False)),
    path("projetos/", include(("projetos.urls", "projetos"), namespace="projetos")),
]