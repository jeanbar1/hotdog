"""
Django settings for cardapio project.
"""

import os
from pathlib import Path
import dj_database_url
from decouple import config
from storages.backends.s3boto3 import S3Boto3Storage

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# ==================== CONFIGURAÇÕES DE SEGURANÇA ====================
SECRET_KEY = config('SECRET_KEY', default='chave-local-dev-so-para-testes')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = ['*']
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.app",
    "https://*.onrender.com",
    "http://localhost:8000"
]

# ==================== CONFIGURAÇÃO DO AMAZON S3 ====================
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='cardapiohot')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-2')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False

# ==================== CONFIGURAÇÕES DE ARMAZENAMENTO ====================
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ==================== CONFIGURAÇÕES DE APLICAÇÃO ====================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'whitenoise.runserver_nostatic',
    'produto',
    'pedido',
    'usuario',
    'carrinho',
    'principal',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cardapio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cardapio.wsgi.application'

# ==================== BANCO DE DADOS ====================
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', 'postgresql://jean_user:12345@localhost:5432/cardapio'),
        conn_max_age=600
    )
}

# ==================== ARQUIVOS ESTÁTICOS E MÍDIA ====================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
MEDIA_ROOT = ''

# ==================== CONFIGURAÇÕES ADICIONAIS ====================
AUTH_USER_MODEL = 'usuario.Usuario'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/usuario/user_login/'

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# ==================== CONFIGURAÇÕES DE PRODUÇÃO ====================
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')