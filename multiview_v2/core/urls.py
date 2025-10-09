from django.urls import path
from django.contrib.auth import views as auth_views
from .views import principal, health, creditos, guias, usuario, usuarios

app_name = "core"

urlpatterns = [
    path("", principal, name="principal"),
    path("principal/", principal, name="principal_explicit"),
    path("health/", health, name="health"),
    path("creditos/", creditos, name="creditos"),
    path("guias/", guias, name="guias"),
    path("usuario/", usuario, name="usuario"),
    path("usuarios/", usuarios, name="usuarios"),

    # Auth
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="core:principal"),
        name="logout",
    ),
]