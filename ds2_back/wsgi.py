"""
WSGI config for ds2_back project.
"""
import os
from django.core.wsgi import get_wsgi_application

# Para producción, asegurar que use settings de producción
os.environ.setdefault('DJANGO_ENV', 'production')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')

application = get_wsgi_application()


