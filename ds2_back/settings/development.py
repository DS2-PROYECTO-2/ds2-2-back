from .base import *

# Carga el .env desde la raíz del proyecto
environ.Env.read_env(BASE_DIR / '.env')

# DEBUG siempre True en desarrollo
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'testserver']

# Database PostgreSQL local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='127.0.0.1'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# CORS para desarrollo
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_CREDENTIALS = True

# Email para desarrollo - Gmail SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='sado56hdgm@gmail.com')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='orfl vkzn dern pbos')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='Soporte DS2 <sado56hdgm@gmail.com>')
EMAIL_TIMEOUT = 20
EMAIL_FAIL_SILENTLY = False

# Brevo API Key para desarrollo (opcional, para testing)
BREVO_API_KEY = env('BREVO_API_KEY', default='')

# URLs para desarrollo
PUBLIC_BASE_URL = "http://localhost:8000"
FRONTEND_BASE_URL = "http://localhost:5173"

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
]

# Deshabilitar CSRF para desarrollo (APIs)
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [
    'rest_framework.authentication.TokenAuthentication',
]