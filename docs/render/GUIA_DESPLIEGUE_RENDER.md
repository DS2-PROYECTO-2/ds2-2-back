# 🚀 Guía de Despliegue en Render

Esta guía te llevará paso a paso para desplegar tu backend de Django en Render.

## 📋 Prerequisitos

- ✅ Cuenta en [GitHub](https://github.com) con tu repositorio
- ✅ Cuenta en [Render](https://render.com) (gratuita)
- ✅ Tu código en la rama `produccion` o `main`
- ✅ Variables de entorno preparadas

## 🎯 Paso 1: Preparar el Repositorio

### 1.1 Verifica que tengas estos archivos:

```bash
# Verifica que existan estos archivos
ls build.sh        # ✅ Script de construcción
ls render.yaml     # ✅ Configuración de Render
ls requirements.txt # ✅ Dependencias Python
ls .env.example    # ✅ Ejemplo de variables de entorno
```

### 1.2 Sube los cambios a GitHub:

```bash
git add .
git commit -m "Preparar para despliegue en Render"
git push origin produccion
```

## 🗄️ Paso 2: Crear Base de Datos PostgreSQL en Render

### 2.1 Accede a Render Dashboard:
1. Ve a [https://dashboard.render.com](https://dashboard.render.com)
2. Haz clic en **"New +"** → **"PostgreSQL"**

### 2.2 Configura la base de datos:
- **Name**: `ds2-database` (o el nombre que prefieras)
- **Database**: `ds2_db`
- **User**: (se genera automáticamente)
- **Region**: Elige la más cercana (ej: `Oregon (US West)`)
- **Plan**: **Free** (0 USD/mes)
- Haz clic en **"Create Database"**

### 2.3 Guarda la información de conexión:
Una vez creada, verás estas credenciales (¡guárdalas!):
```
Internal Database URL: postgresql://user:pass@host/db
External Database URL: postgresql://user:pass@host/db
PSQL Command: psql -h host -U user db
```

> ⚠️ **IMPORTANTE**: La base de datos gratuita expira después de 90 días. Render te avisará antes.

## 🌐 Paso 3: Crear el Web Service

### 3.1 Crear nuevo servicio:
1. En el dashboard de Render, haz clic en **"New +"** → **"Web Service"**
2. Conecta tu repositorio de GitHub:
   - Si es tu primera vez, autoriza a Render a acceder a GitHub
   - Busca tu repositorio: `ds2-2-back`
   - Haz clic en **"Connect"**

### 3.2 Configura el servicio:

#### Configuración Básica:
- **Name**: `ds2-backend` (será parte de tu URL)
- **Region**: Misma que tu base de datos (ej: `Oregon (US West)`)
- **Branch**: `produccion` (o `main`)
- **Root Directory**: (déjalo vacío)
- **Runtime**: **Python 3**
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn ds2_back.wsgi:application`

#### Plan:
- **Instance Type**: **Free** (0 USD/mes)

> ⚠️ **NOTA**: El plan gratuito se suspende después de 15 minutos de inactividad. Se reactiva automáticamente al recibir una solicitud (puede tardar ~30 segundos).

### 3.3 NO hagas clic en "Create Web Service" todavía
Primero configuraremos las variables de entorno.

## 🔐 Paso 4: Configurar Variables de Entorno

### 4.1 En la página de configuración del servicio:
Baja hasta la sección **"Environment Variables"** y agrega estas variables:

#### Variables Esenciales:

```bash
# Django Configuration
SECRET_KEY=tu-clave-secreta-generada-aqui-muy-larga-y-segura
DEBUG=False
ALLOWED_HOSTS=.onrender.com

# Database (se conecta automáticamente)
DATABASE_URL=${ds2-database.DATABASE_URL}

# URLs
PUBLIC_BASE_URL=https://ds2-backend.onrender.com
FRONTEND_BASE_URL=https://tu-frontend.vercel.app

# CSRF Protection
CSRF_TRUSTED_ORIGINS=https://ds2-backend.onrender.com,https://tu-frontend.vercel.app

# Email Configuration
EMAIL_HOST_USER=sado56hdgm@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-de-aplicacion
DEFAULT_FROM_EMAIL=Sistema DS2 <sado56hdgm@gmail.com>

# Python Version
PYTHON_VERSION=3.11.0
```

#### Variables Opcionales (para crear superusuario automáticamente):

```bash
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=tu-password-seguro
DJANGO_SUPERUSER_EMAIL=admin@example.com
```

### 4.2 Generar SECRET_KEY segura:
En tu terminal local, ejecuta:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copia el resultado y úsalo como valor de `SECRET_KEY`.

### 4.3 Configurar DATABASE_URL:
En lugar de escribir toda la URL, usa la referencia interna:
```
${ds2-database.DATABASE_URL}
```
Esto conecta automáticamente con tu base de datos de Render.

## 🚀 Paso 5: Desplegar

### 5.1 Crear el servicio:
1. Revisa que todas las variables estén correctas
2. Haz clic en **"Create Web Service"**
3. Render comenzará el despliegue automáticamente

### 5.2 Monitorear el despliegue:
Verás los logs en tiempo real:
```
==> Installing dependencies from requirements.txt
==> Running build command: ./build.sh
==> Collecting static files...
==> Running migrations...
==> Starting server...
```

El despliegue puede tardar **3-5 minutos** la primera vez.

### 5.3 Verificar estado:
Cuando el despliegue termine exitosamente, verás:
- 🟢 **"Live"** en el badge del servicio
- URL de tu API: `https://ds2-backend.onrender.com`

## ✅ Paso 6: Verificar el Despliegue

### 6.1 Probar endpoints:

#### Health Check:
```bash
curl https://ds2-backend.onrender.com/api/
```

Respuesta esperada:
```json
{
  "message": "API funcionando correctamente",
  "version": "1.0.0"
}
```

#### Admin Panel:
Abre en tu navegador:
```
https://ds2-backend.onrender.com/admin/
```

#### API Documentation:
```
https://ds2-backend.onrender.com/api/schema/swagger-ui/
```

### 6.2 Verificar la base de datos:

#### Opción A - Desde Render Shell:
1. En el dashboard de tu servicio, ve a **"Shell"**
2. Ejecuta:
```bash
python manage.py shell
```
```python
from users.models import User
print(f"Total usuarios: {User.objects.count()}")
```

#### Opción B - Desde terminal local:
Conecta directamente a la base de datos con el comando PSQL que guardaste en el Paso 2.3.

## 🔧 Paso 7: Comandos Útiles Post-Despliegue

### 7.1 Crear superusuario manualmente:
Si no configuraste las variables DJANGO_SUPERUSER_*:

1. Ve a tu servicio en Render
2. Haz clic en **"Shell"** (esquina superior derecha)
3. Ejecuta:
```bash
python manage.py createsuperuser
```
4. Sigue las instrucciones

### 7.2 Ejecutar migraciones manualmente:
```bash
python manage.py migrate
```

### 7.3 Ver variables de entorno:
```bash
python manage.py shell -c "from django.conf import settings; print(settings.DATABASES)"
```

### 7.4 Recolectar archivos estáticos:
```bash
python manage.py collectstatic --no-input
```

## 🔄 Paso 8: Actualizaciones Futuras

### 8.1 Despliegue automático:
Render se conecta a tu rama de GitHub. Cada vez que hagas push:
```bash
git push origin produccion
```
Render detectará los cambios y desplegará automáticamente.

### 8.2 Despliegue manual:
En el dashboard de Render:
1. Ve a tu servicio
2. Haz clic en **"Manual Deploy"** → **"Deploy latest commit"**

### 8.3 Ver logs:
En el dashboard:
- Pestaña **"Logs"**: logs en tiempo real
- Filtra por tipo: Info, Warning, Error

## 🛠️ Solución de Problemas Comunes

### Problema 1: Error "Bad Request (400)"
**Causa**: `ALLOWED_HOSTS` no incluye tu dominio de Render.

**Solución**:
```bash
ALLOWED_HOSTS=.onrender.com,ds2-backend.onrender.com
```

### Problema 2: Error 500 - Static files not found
**Causa**: `collectstatic` no se ejecutó correctamente.

**Solución**:
1. Ve a Shell en Render
2. Ejecuta: `python manage.py collectstatic --no-input`

### Problema 3: Error de conexión a base de datos
**Causa**: `DATABASE_URL` incorrecta.

**Solución**:
1. Ve a tu base de datos en Render
2. Copia la "Internal Database URL"
3. Actualiza la variable `DATABASE_URL` en tu servicio

### Problema 4: CSRF verification failed
**Causa**: `CSRF_TRUSTED_ORIGINS` no incluye tu frontend.

**Solución**:
```bash
CSRF_TRUSTED_ORIGINS=https://ds2-backend.onrender.com,https://tu-frontend.vercel.app
```

### Problema 5: El servicio está "sleeping"
**Causa**: Plan gratuito se suspende después de 15 minutos.

**Solución**: 
- Es normal en plan gratuito
- El servicio se reactiva automáticamente al recibir una solicitud
- Primera solicitud puede tardar 30-60 segundos

### Problema 6: Build fails - "Permission denied: ./build.sh"
**Causa**: El archivo build.sh no tiene permisos de ejecución.

**Solución**:
```bash
git update-index --chmod=+x build.sh
git commit -m "Dar permisos de ejecución a build.sh"
git push origin produccion
```

## 📊 Monitoreo y Mantenimiento

### Métricas disponibles (Dashboard de Render):
- **CPU Usage**: Uso de procesador
- **Memory Usage**: Uso de memoria RAM
- **HTTP Response Time**: Tiempo de respuesta
- **HTTP Status Codes**: Códigos de estado de respuestas

### Alertas recomendadas:
- Configura notificaciones por email en **Settings** → **Notifications**
- Render te avisará si:
  - El despliegue falla
  - El servicio está caído
  - La base de datos está por expirar (90 días)

## 🔒 Seguridad en Producción

### Checklist de seguridad:
- ✅ `DEBUG=False` en producción
- ✅ `SECRET_KEY` única y segura (min 50 caracteres)
- ✅ `ALLOWED_HOSTS` configurado correctamente
- ✅ `CSRF_TRUSTED_ORIGINS` solo con dominios confiables
- ✅ HTTPS habilitado (Render lo hace automáticamente)
- ✅ Variables sensibles en Environment Variables, NO en el código
- ✅ `.env` en `.gitignore` (no subir a GitHub)

## 📞 Recursos y Ayuda

### Documentación oficial:
- [Render Django Docs](https://render.com/docs/deploy-django)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)

### Comandos de diagnóstico:
```bash
# Ver configuración actual
python manage.py check --deploy

# Ver migraciones pendientes
python manage.py showmigrations

# Ver configuración de base de datos
python manage.py dbshell
```

## 🎉 ¡Listo!

Tu backend de Django está ahora desplegado en producción. 

**URL de tu API**: `https://ds2-backend.onrender.com`

**Próximos pasos**:
1. ✅ Configura tu frontend para apuntar a esta URL
2. ✅ Prueba todos los endpoints desde Postman
3. ✅ Crea datos de prueba en el admin panel
4. ✅ Configura monitoreo y alertas

---

**¿Problemas?** Revisa los logs en el dashboard de Render o consulta la sección de solución de problemas.
