
# core/settings.py
from pathlib import Path
import os
import dj_database_url

# Só aplica OSGeo4W se estiver no Windows (dev local)
if os.name == "nt":
    try:
        os.add_dll_directory(r"C:\OSGeo4W\bin")
        os.environ["PATH"] = os.environ.get("PATH", "") + r";C:\OSGeo4W\bin"
        os.environ.setdefault("PROJ_LIB", r"C:\OSGeo4W\share\proj")
        os.environ.setdefault("GDAL_DATA", r"C:\OSGeo4W\share\gdal")
    except Exception:
        pass

# === Paths / Base ===
BASE_DIR = Path(__file__).resolve().parent.parent


# === Autenticação / Redirects ===
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "projetos:index"
LOGOUT_REDIRECT_URL = "login"

# === Segurança / Debug ===
SECRET_KEY = os.getenv("SECRET_KEY", "dev")
DEBUG = os.getenv("DJANGO_DEBUG", "0") == "1"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]").split(",")]

# === Apps ===
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",          # mantém PostGIS/GDAL

    # Terceiros
    "rest_framework",

    # Projeto
    "projetos",
    "core",
    "catalogo",
    "processamento",
    "uploads_datasets",
]

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:8000", "http://localhost:8000"]

# === Middleware ===
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Cookies não seguros em dev (HTTP)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
# (opcional) deixar explícito os defaults:
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False

# MIDDLEWARE deve conter o CsrfViewMiddleware (padrão do Django)
# 'django.middleware.csrf.CsrfViewMiddleware',


# === URLs / WSGI / ASGI ===
ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

# === Templates ===
BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Coloque aqui o diretório de templates do core
        "DIRS": [BASE_DIR / "core" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
            ],
        },
    },
]
# === Banco de Dados (PostGIS) ===
DEFAULT_DB_URL = "postgis://multiview:multiview@db:5432/multiview"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"

# Correção defensiva no Docker (garante host/porta corretos dentro da rede)
if os.path.exists("/.dockerenv"):
    d = DATABASES["default"]
    host = (d.get("HOST") or "").strip().lower()
    port = str(d.get("PORT") or "").strip()
    if host in ("", "127.0.0.1", "localhost"):
        d["HOST"] = "db"
    if port in ("", "none", "5433", ""):
        d["PORT"] = "5432"

# === Idioma / Fuso ===
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# === Static / Media ===
# Estáticos
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "core" / "static"]  # NÃO inclua STATIC_ROOT aqui
STATIC_ROOT = BASE_DIR / "staticfiles"

# Auth
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "projetos:index"
LOGOUT_REDIRECT_URL = "login"



MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# === S3 / MinIO ===
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "multiview")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "senha_123")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://127.0.0.1:9000")
S3_BROWSER_ENDPOINT = os.getenv("S3_BROWSER_ENDPOINT", "http://127.0.0.1:9000")
S3_BUCKET = os.getenv("S3_BUCKET", "multiview-data")
S3_REGION = os.getenv("S3_REGION", "us-east-1")

S3 = {
    "endpoint": S3_ENDPOINT_URL,
    "bucket": S3_BUCKET,
    "access": S3_ACCESS_KEY,
    "secret": S3_SECRET_KEY,
    "region": S3_REGION,
    "public_url": f"{S3_BROWSER_ENDPOINT}/{S3_BUCKET}",
}

# Aliases AWS (caso alguma lib espere esses nomes)
AWS_S3_ENDPOINT_URL = S3_ENDPOINT_URL
AWS_ACCESS_KEY_ID = S3_ACCESS_KEY
AWS_SECRET_ACCESS_KEY = S3_SECRET_KEY
AWS_STORAGE_BUCKET_NAME = S3_BUCKET
AWS_S3_REGION_NAME = S3_REGION

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ===================== GDAL/GEOS (Windows via OSGeo4W) =====================
# O Django lê GDAL_LIBRARY_PATH/GEOS_LIBRARY_PATH a partir do settings.py.
# Se você já exportou as variáveis no PowerShell, mantenha — mas este bloco
# garante que o Django saiba os caminhos mesmo sem o shell.

import os

OSGEO_ROOT = os.environ.get("OSGEO4W_ROOT") or r"C:\OSGeo4W"

# Caminhos das DLLs (ajuste se o seu OSGeo estiver em outro lugar ou versão)
GDAL_LIBRARY_PATH = os.environ.get("GDAL_LIBRARY_PATH") or fr"{OSGEO_ROOT}\bin\gdal311.dll"
GEOS_LIBRARY_PATH = os.environ.get("GEOS_LIBRARY_PATH") or fr"{OSGEO_ROOT}\bin\geos_c.dll"

# Dados do PROJ/GDAL e PATH para dependências das DLLs
os.environ.setdefault("PROJ_LIB", fr"{OSGEO_ROOT}\share\proj")
os.environ.setdefault("GDAL_DATA", fr"{OSGEO_ROOT}\share\gdal")
os.environ.setdefault("PATH", fr"{OSGEO_ROOT}\bin;" + os.environ.get("PATH", ""))
# ========================================================================

# ===================== DATABASES (PostGIS local) =====================
import os

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ.get("PGDATABASE", "multiview"),
        "USER": os.environ.get("PGUSER", "multiview"),
        "PASSWORD": os.environ.get("PGPASSWORD", "multiview"),
        # Se estava vindo "db" ou vazio, força 127.0.0.1:
        "HOST": os.environ.get("PGHOST", "127.0.0.1"),
        "PORT": os.environ.get("PGPORT", "5432"),
        # Opcional: evita tentativa de SSL local
        "OPTIONS": {"sslmode": "disable"},
    }
}
# =====================================================================