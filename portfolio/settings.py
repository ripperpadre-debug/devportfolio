from pathlib import Path
import os
import shutil
import tempfile
from urllib.parse import unquote, urlparse

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
SECRET_KEY = 'django-insecure-change-this-in-production-use-env-variable'
DEBUG = True
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = [
    'https://*.replit.dev',
    'https://*.repl.co',
    'https://*.spock.replit.dev',
    'http://localhost:5000',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'portfolio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_profile',
            ],
        },
    },
]

WSGI_APPLICATION = 'portfolio.wsgi.application'


def sqlite_sync_source_path():
    source_path = Path(os.environ.get('SQLITE_SYNC_SOURCE', BASE_DIR / 'db.sqlite3'))
    if not source_path.is_absolute():
        source_path = BASE_DIR / source_path
    return source_path


def _sqlite_db_path(candidate_path):
    path = Path(candidate_path).expanduser()
    if path.exists() and not os.access(path.parent, os.W_OK):
        fallback_path = Path(tempfile.gettempdir()) / path.name
        if path.exists():
            try:
                shutil.copy2(path, fallback_path)
            except OSError:
                pass
        return fallback_path

    if not path.exists():
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
            path.unlink(missing_ok=True)
        except OSError:
            fallback_path = Path(tempfile.gettempdir()) / path.name
            if path.exists():
                try:
                    shutil.copy2(path, fallback_path)
                except OSError:
                    pass
            return fallback_path

    return path


def sqlite_database_config():
    configured_path = os.environ.get('SQLITE_DB_PATH')
    if configured_path:
        db_path = _sqlite_db_path(configured_path)
    else:
        db_path = _sqlite_db_path(BASE_DIR / 'db.sqlite3')

    db_path.parent.mkdir(parents=True, exist_ok=True)
    return {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': db_path,
    }


def resolve_media_root(configured_path=None):
    candidate = Path(configured_path or os.environ.get('MEDIA_ROOT') or BASE_DIR / 'media')
    if not candidate.is_absolute():
        candidate = BASE_DIR / candidate

    try:
        candidate.mkdir(parents=True, exist_ok=True)
        if os.access(candidate, os.W_OK):
            with tempfile.NamedTemporaryFile(dir=str(candidate), delete=True) as handle:
                handle.write(b'.')
            return candidate
    except OSError:
        pass

    fallback = Path(tempfile.gettempdir()) / 'devportfolio-media'
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def postgres_database_config_from_url(database_url):
    parsed = urlparse(database_url)
    config = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': unquote(parsed.path.lstrip('/')),
        'USER': unquote(parsed.username or ''),
        'PASSWORD': unquote(parsed.password or ''),
        'HOST': parsed.hostname or '',
        'PORT': str(parsed.port or ''),
    }
    query_params = {}
    for item in parsed.query.split('&'):
        if '=' in item:
            key, value = item.split('=', 1)
            query_params[key] = unquote(value)
    if 'sslmode' in query_params:
        config['OPTIONS'] = {'sslmode': query_params['sslmode']}
    elif parsed.hostname and '.neon.tech' in parsed.hostname:
        config['OPTIONS'] = {'sslmode': 'require'}
    return config


def postgres_database_config_from_env():
    database_name = os.environ.get('POSTGRES_DB') or os.environ.get('PGDATABASE')
    if not database_name:
        return None

    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': database_name,
        'USER': os.environ.get('POSTGRES_USER') or os.environ.get('PGUSER', ''),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD') or os.environ.get('PGPASSWORD', ''),
        'HOST': os.environ.get('POSTGRES_HOST') or os.environ.get('PGHOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT') or os.environ.get('PGPORT', '5432'),
    }


def database_config():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        return postgres_database_config_from_url(database_url)

    postgres_config = postgres_database_config_from_env()
    if postgres_config:
        return postgres_config

    return sqlite_database_config()


DATABASES = {
    'default': database_config(),
    'sqlite_source': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': sqlite_sync_source_path(),
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'core' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = resolve_media_root()

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Social Media API Keys (set via environment variables or .env file)
TWITTER_BEARER_TOKEN = os.environ.get('TWITTER_BEARER_TOKEN', '')
TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY', '')
TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET', '')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN', '')
TWITTER_ACCESS_SECRET = os.environ.get('TWITTER_ACCESS_SECRET', '')

LINKEDIN_ACCESS_TOKEN = os.environ.get('LINKEDIN_ACCESS_TOKEN', '')
LINKEDIN_PERSON_ID = os.environ.get('LINKEDIN_PERSON_ID', '')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
NOTIFY_EMAIL = os.environ.get('NOTIFY_EMAIL', EMAIL_HOST_USER)
