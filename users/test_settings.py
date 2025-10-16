# Configuración específica para tests
from .settings import *

# Configuración de email para tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Brevo API Key para tests (usar una key de prueba o mock)
BREVO_API_KEY = 'test_brevo_api_key_for_testing'

# Configuración de testing
TESTING = True
DEBUG = True
