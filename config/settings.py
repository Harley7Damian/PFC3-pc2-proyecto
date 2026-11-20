"""Configuración de CicloSeguro Lima.

Todo valor sensible llega por variables de entorno (SECRET_KEY, DATABASE_URL, ALLOWED_HOSTS).
En producción (Render) DEBUG=0 y se activan HTTPS, cookies seguras, HSTS y CSP.
"""
import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from django.utils.csp import CSP

BASE_DIR = Path(__file__).resolve().parent.parent

# Render define RENDER=true: allí nunca se permite DEBUG, aunque falte la variable.
EN_RENDER = os.environ.get("RENDER", "").lower() == "true"
DEBUG = os.environ.get("DEBUG", "1") == "1" and not EN_RENDER

SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "clave-solo-para-desarrollo-local"
    else:
        raise ImproperlyConfigured("Falta la variable de entorno SECRET_KEY.")

ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = []
host_render = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "")
if host_render:
    ALLOWED_HOSTS.append(host_render)
    CSRF_TRUSTED_ORIGINS.append("https://" + host_render)
if DEBUG:
    ALLOWED_HOSTS += ["localhost", "127.0.0.1", "testserver"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "axes",
    "core",
    "cuentas",
    "rutas",
    "incidentes",
    "estacionamientos",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.csp.ContentSecurityPolicyMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.csp",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Base de datos: DATABASE_URL (PostgreSQL en Neon o Supabase). Sin variable, SQLite local.
DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///%s" % (BASE_DIR / "db.sqlite3"),
        conn_max_age=600,
    )
}

# Contraseñas: PBKDF2 (hasher por defecto de Django) y validadores activos.
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Límite de intentos de ingreso (django-axes): 5 fallos por correo e IP bloquean 15 minutos.
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 0.25
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]
AXES_RESET_ON_SUCCESS = True
AXES_ENABLED = os.environ.get("AXES_ENABLED", "1") == "1"

LOGIN_URL = "cuentas:ingresar"
LOGIN_REDIRECT_URL = "core:inicio"
LOGOUT_REDIRECT_URL = "core:inicio"

LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        if DEBUG
        else "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Cabeceras y cookies seguras (siempre) y HTTPS estricto (solo en producción).
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# Política de contenido: solo recursos propios, sin scripts ni estilos en línea.
SECURE_CSP = {
    "default-src": [CSP.SELF],
    "script-src": [CSP.SELF],
    "style-src": [CSP.SELF],
    "img-src": [CSP.SELF, "data:"],
    "frame-ancestors": [CSP.NONE],
    "form-action": [CSP.SELF],
    "base-uri": [CSP.SELF],
}

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SECURE_REDIRECT_EXEMPT = [r"^salud/$"]
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

AXES_LOCKOUT_TEMPLATE = "cuentas/bloqueado.html"
