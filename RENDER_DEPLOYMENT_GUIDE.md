# 🚀 Guía de Despliegue en Render - DS2 Backend

## 📋 Archivos Creados para Despliegue

### ✅ Archivos de Configuración Creados:

1. **`ds2_back/settings_production.py`** - Configuración de producción
2. **`build.sh`** - Script de construcción para Render
3. **`Procfile`** - Configuración de procesos
4. **`runtime.txt`** - Versión de Python
5. **`requirements.txt`** - Actualizado con dependencias de producción

## 🔧 Configuración en Render

### Paso 1: Crear Servicio Web
1. Ir a [render.com](https://render.com)
2. Conectar repositorio GitHub/GitLab
3. Seleccionar "Web Service"
4. Configurar:

```
Name: ds2-backend
Environment: Python 3
Build Command: ./build.sh
Start Command: gunicorn ds2_back.wsgi:application
```

### Paso 2: Variables de Entorno
Agregar estas variables en Render Dashboard:

```bash
# Django Settings
SECRET_KEY=tu-secret-key-muy-largo-y-seguro-aqui
DEBUG=False
ALLOWED_HOSTS=ds2-backend.onrender.com

# Database (se genera automáticamente al crear PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:port/db

# Email Configuration
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=Soporte DS2 <noreply@ds2-backend.onrender.com>

# URLs
PUBLIC_BASE_URL=https://ds2-backend.onrender.com
FRONTEND_BASE_URL=https://ds2-frontend.onrender.com
```

### Paso 3: Crear Base de Datos PostgreSQL
1. En Render Dashboard, crear "PostgreSQL"
2. Copiar la `DATABASE_URL` generada
3. Agregarla a las variables de entorno del servicio web

## 🏗️ Proceso de Despliegue

### Build Process (automático):
```bash
# Render ejecutará automáticamente:
./build.sh
```

### Start Process:
```bash
# Render iniciará con:
gunicorn ds2_back.wsgi:application --bind 0.0.0.0:$PORT
```

## 📊 Configuración de Producción

### Características Incluidas:
- ✅ **SSL/HTTPS** automático
- ✅ **Static files** con WhiteNoise
- ✅ **Database migrations** automáticas
- ✅ **Logging** configurado
- ✅ **Security headers** habilitados
- ✅ **CORS** configurado
- ✅ **Rate limiting** implementado

### URLs Generadas:
- **Backend API**: `https://ds2-backend.onrender.com`
- **Admin Panel**: `https://ds2-backend.onrender.com/admin/`
- **API Docs**: `https://ds2-backend.onrender.com/api/schema/`

## 🔐 Seguridad Implementada

### Headers de Seguridad:
- `SECURE_SSL_REDIRECT=True`
- `SECURE_PROXY_SSL_HEADER`
- `SESSION_COOKIE_SECURE=True`
- `CSRF_COOKIE_SECURE=True`
- `X_FRAME_OPTIONS=DENY`

### Rate Limiting:
- Anónimos: 100 requests/hora
- Usuarios: 1000 requests/hora

## 📈 Monitoreo y Logs

### En Render Dashboard:
- **Logs en tiempo real**
- **Métricas de rendimiento**
- **Estado del servicio**
- **Restart automático**

### Logs de Aplicación:
- Archivo: `logs/django.log`
- Console: Stream en Render Dashboard
- Nivel: INFO

## ⚠️ Consideraciones Importantes

### Plan Gratuito (Limitaciones):
- **Sleep después de 15 min** de inactividad
- **Cold start** puede tomar 30+ segundos
- **Límite de 750 horas/mes**

### Para Producción Real:
- **Upgrade a plan pago** ($7/mes)
- **Configurar dominio personalizado**
- **Implementar cache Redis**
- **Configurar backup automático**

## 🚀 Comandos de Despliegue

### Despliegue Manual:
```bash
# 1. Commit cambios
git add .
git commit -m "Preparar para despliegue en Render"
git push origin main

# 2. Render detectará cambios automáticamente
# 3. Ejecutará build.sh
# 4. Iniciará el servicio
```

### Verificación Post-Despliegue:
```bash
# Verificar que el servicio esté funcionando
curl https://ds2-backend.onrender.com/api/health/

# Verificar admin
curl https://ds2-backend.onrender.com/admin/

# Verificar API
curl https://ds2-backend.onrender.com/api/rooms/
```

## 💰 Costos Estimados

- **Plan Gratuito**: $0/mes (con limitaciones)
- **Plan Starter**: $7/mes (sin sleep)
- **PostgreSQL**: $7/mes (base de datos)
- **Total**: $0-14/mes

## 🎯 Próximos Pasos

1. **Crear servicio en Render**
2. **Configurar variables de entorno**
3. **Crear base de datos PostgreSQL**
4. **Hacer push del código**
5. **Verificar despliegue**
6. **Configurar dominio personalizado** (opcional)

## 📞 Soporte

Si tienes problemas con el despliegue:
1. Revisar logs en Render Dashboard
2. Verificar variables de entorno
3. Comprobar configuración de base de datos
4. Verificar que todos los archivos estén en el repositorio

¡El backend está listo para desplegarse en Render! 🎉
