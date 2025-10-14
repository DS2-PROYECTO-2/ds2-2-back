from .base import *

# Configuración específica para tests
DEBUG = False

# Base de datos SQLite en memoria para tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
            'timeout': 20,
        },
    }
}

# Configuración mínima para tests
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# Email backend para tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# URLs para tests
PUBLIC_BASE_URL = "http://testserver"
FRONTEND_BASE_URL = "http://testserver"

# Deshabilitar migraciones para tests más rápidos
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Password hashers más rápidos para tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Cache en memoria para tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Logging mínimo para tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}