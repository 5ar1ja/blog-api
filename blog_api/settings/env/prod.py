from settings.base import *

# Согласно ТЗ: prod.py — sets DEBUG=False, PostgreSQL, etc.
DEBUG = False

# Здесь ОБЯЗАТЕЛЬНО должны быть указаны хосты, иначе будет ошибка, которую ты видел
ALLOWED_HOSTS = config("BLOG_ALLOWED_HOSTS", cast=list, default=[])

# Настройки PostgreSQL (данные берем из конфига/env)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("BLOG_DB_NAME"),
        "USER": config("BLOG_DB_USER"),
        "PASSWORD": config("BLOG_DB_PASSWORD"),
        "HOST": config("BLOG_DB_HOST"),
        "PORT": config("BLOG_DB_PORT"),
    }
}

# Включаем обязательную защиту для продакшена
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True