
# core/settings.py
from pathlib import Path
from glob import glob
import os
import dj_database_url

# -----------------------------------------------------------------------------
# Caminhos base
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# Integração OSGeo4W (Windows) – GDAL/GEOS/PROJ
# Somente em Windows (desenvolvimento local). No Linux/Docker, ignore.
# -----------------------------------------------------------------------------
if os.name == "nt":
    OSGEO_ROOT = os.environ.get("OSGEO4W_ROOT") or r"C:\OSGeo4W"
    BIN_DIR = os.path.join(OSGEO_ROOT, "bin")
    try:
        os.add_dll_directory(BIN_DIR)
    except Exception:
        pass
    def _pick_one(pattern: str):
        files = sorted(glob(os.path.join(BIN_DIR, pattern)), reverse=True)
        return files[0] if files else None

    # Escolhe automaticamente a DLL instalada (ex.: gdal311.dll)
    _gdal = _pick_one("gdal*.dll")
    _geos = _pick_one("geos_c*.dll") or _pick_one("geos_c.dll")

    # Expõe como SETTINGS que o Django GIS lê!
    # (Se não encontrar, mantenha None — Django cairá no fallback e veremos o erro claramente)
    GDAL_LIBRARY_PATH = _gdal
    GEOS_LIBRARY_PATH = _geos

    # Variáveis de dados do PROJ/GDAL (usadas por dependências do GDAL)
    os.environ.setdefault("PROJ_LIB", os.path.join(OSGEO_ROOT, "share", "proj"))
    os.environ.setdefault("GDAL_DATA", os.path.join(OSGEO_ROOT, "share", "gdal"))

    # Também ajuda o carregador tradicional de DLLs
    os.environ["PATH"] = BIN_DIR + ";" + os.environ.get("PATH", "")
# -----------------------------------------------------------------------------
# Segurança / Debug
# -----------------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev")
DEBUG = os.getenv("DJANGO_DEBUG", "0") == "1"

ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost,[::1]").split(",")
]
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "http://localhost",
    "http://localhost:8000",
]

# Cookies inseguros em dev (HTTP):
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False
SECURE_CONTENT_TYPE_NOSNIFF = True

# -----------------------------------------------------------------------------
# Apps
# -----------------------------------------------------------------------------

DEBUG = True

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",  # PostGIS/GDAL



    # Terceiros
    "rest_framework",

    # Projeto
    "core",
    "projetos",
    "catalogo",
    "processamento",
    "uploads_datasets",
]

if DEBUG:
    INSTALLED_APPS += ["django_extensions"]
# -----------------------------------------------------------------------------
# Middleware
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -----------------------------------------------------------------------------
# URLs / WSGI / ASGI
# -----------------------------------------------------------------------------
ROOT_URLCONF = "core.urls_root"
WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "http://localhost",
    "http://localhost:8000",
]

# -----------------------------------------------------------------------------
# Templates
# -----------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "core" / "templates"],  # base_public.html, etc.
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

# -----------------------------------------------------------------------------
# Banco de Dados (PostGIS)
# - Usa DATABASE_URL se existir; senão cai no Postgres local 127.0.0.1
# - Em Docker (/.dockerenv) sem DATABASE_URL: força host "db"
# -----------------------------------------------------------------------------
def env_first(*names, default=None):
    import os
    for n in names:
        v = os.getenv(n)
        if v: return v
    return default

DEFAULT_DB = {
    "ENGINE": "django.contrib.gis.db.backends.postgis",
    "NAME": env_first("DATABASE_NAME","DB_NAME","POSTGRES_DB","PGDATABASE", default="multiview"),
    "USER": env_first("DATABASE_USER","DB_USER","POSTGRES_USER","PGUSER", default="mv"),
    "PASSWORD": env_first("DATABASE_PASSWORD","DB_PASSWORD","POSTGRES_PASSWORD","PGPASSWORD", default="mvpass123!"),
    "HOST": env_first("DATABASE_HOST","DB_HOST","POSTGRES_HOST","PGHOST", default="127.0.0.1"),
    "PORT": env_first("DATABASE_PORT","DB_PORT","POSTGRES_PORT","PGPORT", default="5432"),
    "CONN_MAX_AGE": 600,
    "OPTIONS": {"sslmode": env_first("DB_SSLMODE","PGSSLMODE", default="disable")},
}

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            engine="django.contrib.gis.db.backends.postgis",
            conn_max_age=600,
        )
    }
else:
    DATABASES = {"default": DEFAULT_DB}

# Ajuste automático em container Docker (se não houver DATABASE_URL)
if os.path.exists("/.dockerenv") and not DATABASE_URL:
    DATABASES["default"]["HOST"] = "db"
    DATABASES["default"]["PORT"] = "5432"


# -----------------------------------------------------------------------------
# Idioma / Fuso
# -----------------------------------------------------------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# Arquivos estáticos e mídia
# -----------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"             # destino do collectstatic

# Só mantenha diretórios GLOBAIS aqui (se existir).
# NÃO coloque diretórios de apps (ex.: BASE_DIR / "core" / "static")!
STATICFILES_DIRS = [
    BASE_DIR / "core" / "static",   # opcional: só se você tiver web/static/
]

# Use os finders padrão (não duplique, não remova)
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Armazenamento de estáticos
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}



MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -----------------------------------------------------------------------------
# Redirects de autenticação
# -----------------------------------------------------------------------------
LOGIN_URL = "core:login"
LOGIN_REDIRECT_URL = "core:principal"
LOGOUT_REDIRECT_URL = "core:login"

# -----------------------------------------------------------------------------
# S3 / MinIO (para uploads)
# -----------------------------------------------------------------------------
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

# aliases esperados por alguns SDKs:
AWS_S3_ENDPOINT_URL = S3_ENDPOINT_URL
AWS_ACCESS_KEY_ID = S3_ACCESS_KEY
AWS_SECRET_ACCESS_KEY = S3_SECRET_KEY
AWS_STORAGE_BUCKET_NAME = S3_BUCKET
AWS_S3_REGION_NAME = S3_REGION

# -----------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DEFAULT_CHARSET = "utf-8"
