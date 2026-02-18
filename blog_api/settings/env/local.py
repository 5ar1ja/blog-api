from settings.base import *
import os

# Согласно ТЗ: local.py — sets DEBUG=True, SQLite, etc.
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Настройки базы данных для разработки
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "碰AME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# Включаем отладочные инструменты только тут
# (Убедись, что эти переменные импортированы из conf.py через base.py)
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

INTERNAL_IPS = ["127.0.0.1"]