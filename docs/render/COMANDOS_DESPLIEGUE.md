# 🚀 Comandos Rápidos para Despliegue en Render

## Pre-Despliegue (Local)

### 1. Generar SECRET_KEY
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Verificar archivos necesarios
```bash
ls build.sh render.yaml requirements.txt .env.example
```

### 3. Dar permisos de ejecución a build.sh
```bash
git update-index --chmod=+x build.sh
```

### 4. Subir cambios a GitHub
```bash
git add .
git commit -m "Preparar para despliegue en Render"
git push origin produccion
```

### 5. Checklist de seguridad
```bash
python manage.py check --deploy
```

## Variables de Entorno en Render

### Copiar y pegar en "Environment Variables":

```bash
# Básicas
SECRET_KEY=genera-una-clave-con-el-comando-de-arriba
DEBUG=False
PYTHON_VERSION=3.11.0
ALLOWED_HOSTS=.onrender.com

# Base de datos (usa la referencia interna)
DATABASE_URL=${ds2-database.DATABASE_URL}

# URLs (reemplaza con tus dominios)
PUBLIC_BASE_URL=https://ds2-backend.onrender.com
FRONTEND_BASE_URL=https://tu-frontend.vercel.app
CSRF_TRUSTED_ORIGINS=https://ds2-backend.onrender.com,https://tu-frontend.vercel.app

# Email
EMAIL_HOST_USER=sado56hdgm@gmail.com
EMAIL_HOST_PASSWORD=tu-password-de-aplicacion
DEFAULT_FROM_EMAIL=Sistema DS2 <sado56hdgm@gmail.com>

# Superusuario (opcional)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=tu-password-seguro
DJANGO_SUPERUSER_EMAIL=admin@example.com
```

## Post-Despliegue (Render Shell)

### Conectarse a Shell
1. Dashboard → Tu servicio → **Shell** (botón arriba a la derecha)

### Crear superusuario
```bash
python manage.py createsuperuser
```

### Ver estado de la base de datos
```bash
python manage.py dbshell
\dt  # Ver todas las tablas
\q   # Salir
```

### Ver migraciones
```bash
python manage.py showmigrations
```

### Aplicar migraciones
```bash
python manage.py migrate
```

### Recolectar archivos estáticos
```bash
python manage.py collectstatic --no-input
```

### Shell de Django
```bash
python manage.py shell
```
```python
# Ver total de usuarios
from users.models import User
User.objects.count()

# Ver configuración
from django.conf import settings
print(settings.DATABASES)
print(settings.DEBUG)
print(settings.ALLOWED_HOSTS)
```

## Pruebas de API (Local)

### Probar con curl
```bash
# Health check
curl https://ds2-backend.onrender.com/api/

# Login
curl -X POST https://ds2-backend.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"tu-password"}'

# Ver usuarios (necesita token)
curl https://ds2-backend.onrender.com/api/users/ \
  -H "Authorization: Token tu-token-aqui"
```

### URLs importantes
```
Admin Panel: https://ds2-backend.onrender.com/admin/
API Root: https://ds2-backend.onrender.com/api/
Swagger Docs: https://ds2-backend.onrender.com/api/schema/swagger-ui/
ReDoc: https://ds2-backend.onrender.com/api/schema/redoc/
```

## Actualizar Despliegue

### Método 1: Push a GitHub (automático)
```bash
git add .
git commit -m "Actualizar backend"
git push origin produccion
# Render detecta el cambio y redespliega automáticamente
```

### Método 2: Manual Deploy
1. Dashboard → Tu servicio
2. Click **Manual Deploy** → **Deploy latest commit**

### Ver logs en tiempo real
1. Dashboard → Tu servicio → **Logs**
2. O desde CLI de Render:
```bash
render logs -s ds2-backend --tail
```

## Debugging

### Ver logs
```bash
# En Dashboard de Render: Logs tab
# Filtrar por nivel: All, Info, Warning, Error
```

### Conectar a PostgreSQL desde local
```bash
# Usa el "PSQL Command" de tu base de datos en Render
psql -h oregon-postgres.render.com -U user ds2_db
```

### Ver variables de entorno actual
```bash
# En Shell de Render:
env | grep -E "DEBUG|SECRET|DATABASE|ALLOWED"
```

### Forzar rebuild
```bash
# Dashboard → Settings → scroll hasta abajo → "Clear build cache"
# Luego hacer Manual Deploy
```

## Monitoreo

### Verificar que el servicio esté activo
```bash
curl -I https://ds2-backend.onrender.com/api/
# Debería retornar: HTTP/2 200
```

### Monitorear uptime
Usar servicios como:
- [UptimeRobot](https://uptimerobot.com) (gratuito)
- [Freshping](https://www.freshworks.com/website-monitoring/) (gratuito)

Configurar ping cada 15 minutos para evitar que el servicio entre en sleep.

## Troubleshooting Rápido

### Error 400 - Bad Request
```bash
# Verificar ALLOWED_HOSTS
ALLOWED_HOSTS=.onrender.com,ds2-backend.onrender.com
```

### Error 500 - Internal Server Error
```bash
# Ver logs en Render
# Normalmente es problema de migraciones o variables de entorno
python manage.py migrate
python manage.py collectstatic --no-input
```

### Error de CSRF
```bash
# Verificar CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS=https://tu-backend.onrender.com,https://tu-frontend.vercel.app
```

### Base de datos no conecta
```bash
# Verificar DATABASE_URL
echo $DATABASE_URL
# Debe tener formato: postgresql://user:pass@host:port/db
```

### Servicio en sleep
```bash
# Es normal en plan gratuito después de 15 min
# Primera solicitud reactiva el servicio (30-60 seg)
# Solución: usar servicio de ping cada 14 minutos
```

## Backup de Base de Datos

### Exportar desde Render
```bash
# Conectar a la base de datos
psql -h host -U user db

# Exportar a SQL
pg_dump -h host -U user -d db > backup.sql

# O desde Dashboard: Database → Backups → Create Manual Backup
```

### Importar backup
```bash
psql -h host -U user -d db < backup.sql
```

## Recursos

- [Dashboard Render](https://dashboard.render.com)
- [Documentación Render](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Render Status](https://status.render.com)

---

💡 **Tip**: Guarda este archivo para referencia rápida durante el despliegue.
