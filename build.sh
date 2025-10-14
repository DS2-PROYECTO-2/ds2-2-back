#!/usr/bin/env bash
# build.sh - Script de construcción para Render

set -o errexit  # Exit en error

# Instalar dependencias
pip install -r requirements.txt

# Configurar entorno de producción
export DJANGO_ENV=production

# Recopilar archivos estáticos
python manage.py collectstatic --clear --no-input

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario si no existe (opcional)
if [[ $CREATE_SUPERUSER ]]; then
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', '$ADMIN_PASSWORD')
    print('Superuser created')
else:
    print('Superuser already exists')
"
fi