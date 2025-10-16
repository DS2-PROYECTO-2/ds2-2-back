from .base import *
import dj_database_url

# Configuración de producción (sin .env)
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

# Base de datos desde DATABASE_URL (Render)
DATABASES = {
    'default': dj_database_url.parse(
        env('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Configuración SSL para PostgreSQL en Render
DATABASES['default']['OPTIONS'] = {
    'sslmode': 'require',
}

# Security settings
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS para producción
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = env.bool('CORS_ALLOW_ALL_ORIGINS', default=False)  # Para testing

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

# Configuración para APIs y testing con Postman
DISABLE_CSRF_FOR_API = env.bool('DISABLE_CSRF_FOR_API', default=False)


# Email para producción - Brevo API
EMAIL_BACKEND = 'anymail.backends.brevo.EmailBackend'
ANYMAIL = {
    'BREVO_API_KEY': env('BREVO_API_KEY', default=''),
}
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='Soporte DS2 <sado56hdgm@gmail.com>')

# URLs para producción
PUBLIC_BASE_URL = env('PUBLIC_BASE_URL')
FRONTEND_BASE_URL = env('FRONTEND_BASE_URL')

# Logging para producción
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}