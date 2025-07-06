from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('DJANGO_SECRET_KEY', default='django-insecure-0peo@#x9jur3!h$ryje!$879xww8y1y66jx!%*#ymhg&jkozs2')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', default=True)

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=["localhost", "0.0.0.0", "127.0.0.1"])

# Database
DATABASES = {
    "default": env.db_url(
        'DATABASE_URL',
        default='postgresql://postgres:postgres@db:5432/postgres'
    )
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', default='root@localhost')

CSRF_TRUSTED_ORIGINS = env.list(
    'CSRF_TRUSTED_ORIGINS',
    default=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
)
