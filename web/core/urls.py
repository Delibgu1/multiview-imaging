
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include


app_name = "core"

urlpatterns = [
    path("", views.home_redirect, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("principal/", views.principal, name="principal"),
    path("creditos/", views.creditos, name="creditos"),
    path("guias/", views.guias, name="guias"),
    path("usuario/", views.usuario, name="usuario"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)