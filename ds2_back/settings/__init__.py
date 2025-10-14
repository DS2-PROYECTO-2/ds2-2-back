"""
Settings selector based on environment
"""
import os

# Determina qué settings usar basándose en variables de entorno
ENVIRONMENT = os.getenv('DJANGO_ENV', 'development')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'testing':
    from .testing import *
else:
    from .development import *