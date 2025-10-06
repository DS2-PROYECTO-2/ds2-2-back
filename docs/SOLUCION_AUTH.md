# 🔧 Solución de Problemas de Autenticación

## 🚨 **Problemas Identificados y Soluciones**

### 1. **Configuración de Email**
**Problema**: Los emails no se envían porque la configuración de email no está bien configurada.

**Solución**:
```python
# En ds2_back/settings.py - YA CORREGIDO
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Para desarrollo
```

### 2. **Variables de Entorno Faltantes**
**Problema**: Las variables de entorno para email no están configuradas.

**Solución**:
```bash
# Crear archivo .env en la raíz del proyecto
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password-app
DEFAULT_FROM_EMAIL=tu-email@gmail.com
```

### 3. **Problemas de Login**
**Problema**: El login no funciona por problemas de verificación.

**Solución**: Los usuarios monitores requieren verificación por un admin.

---

## 🛠️ **Pasos para Solucionar**

### **Paso 1: Verificar Configuración**
```bash
# Ejecutar comando de prueba
python manage.py test_auth --create-test-user --test-email
```

### **Paso 2: Crear Usuarios de Prueba**
```bash
# Crear usuario admin
python manage.py createsuperuser

# O usar el comando de prueba
python manage.py test_auth --create-test-user
```

### **Paso 3: Probar Endpoints**
```bash
# Ejecutar script de prueba
python test_auth_endpoints.py
```

### **Paso 4: Verificar Base de Datos**
```bash
# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Verificar usuarios
python manage.py shell
>>> from users.models import User
>>> User.objects.all()
```

---

## 🔍 **Diagnóstico de Problemas**

### **1. Error de Login**
**Síntomas**: 
- "Usuario no encontrado"
- "Contraseña incorrecta"
- "Cuenta no verificada"

**Soluciones**:
```python
# Verificar usuario existe
User.objects.filter(username='tu_usuario').exists()

# Verificar contraseña
user.check_password('tu_password')

# Verificar verificación
user.is_verified
```

### **2. Error de Email**
**Síntomas**:
- "Error enviando email"
- No se reciben emails de reset

**Soluciones**:
```python
# Verificar configuración
from django.conf import settings
print(settings.EMAIL_BACKEND)
print(settings.EMAIL_HOST_USER)

# Probar envío manual
from django.core.mail import send_mail
send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

### **3. Error de Token**
**Síntomas**:
- "Token inválido"
- "Token expirado"

**Soluciones**:
```python
# Verificar token en base de datos
from users.models import PasswordReset
PasswordReset.objects.filter(token_hash=token_hash).exists()

# Limpiar tokens expirados
python manage.py shell
>>> from users.models import PasswordReset
>>> PasswordReset.objects.filter(expires_at__lt=timezone.now()).delete()
```

---

## 🚀 **Configuración Completa**

### **1. Archivo .env**
```env
# Email Configuration
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password-app
DEFAULT_FROM_EMAIL=tu-email@gmail.com

# URLs
PUBLIC_BASE_URL=http://localhost:8000
FRONTEND_BASE_URL=http://localhost:5173

# Debug
DEBUG=True
```

### **2. Configuración de Gmail**
Para usar Gmail, necesitas:
1. Habilitar "Verificación en 2 pasos"
2. Generar una "Contraseña de aplicación"
3. Usar esa contraseña en `EMAIL_HOST_PASSWORD`

### **3. Configuración de Producción**
```python
# En settings.py para producción
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

---

## 🧪 **Pruebas de Funcionamiento**

### **1. Probar Login**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123456"}'
```

### **2. Probar Reset de Contraseña**
```bash
curl -X POST http://localhost:8000/api/auth/password/reset-request/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@ejemplo.com"}'
```

### **3. Probar Dashboard**
```bash
curl -X GET http://localhost:8000/api/auth/dashboard/ \
  -H "Authorization: Token tu_token_aqui"
```

---

## 📋 **Checklist de Verificación**

- [ ] ✅ Servidor Django ejecutándose
- [ ] ✅ Base de datos migrada
- [ ] ✅ Usuarios de prueba creados
- [ ] ✅ Configuración de email correcta
- [ ] ✅ Endpoints respondiendo
- [ ] ✅ Emails mostrándose en consola
- [ ] ✅ Tokens funcionando
- [ ] ✅ Login exitoso
- [ ] ✅ Reset de contraseña funcionando

---

## 🆘 **Si Aún No Funciona**

### **1. Verificar Logs**
```bash
# Revisar logs del servidor
python manage.py runserver --verbosity=2
```

### **2. Probar en Modo Debug**
```python
# En settings.py
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### **3. Reiniciar Todo**
```bash
# Parar servidor
# Limpiar base de datos
rm db.sqlite3
python manage.py migrate
python manage.py test_auth --create-test-user
python manage.py runserver
```

---

## 🎯 **Usuarios de Prueba Creados**

Después de ejecutar `python manage.py test_auth --create-test-user`:

- **Admin**: `admin` / `admin123456`
- **Monitor**: `monitor` / `monitor123456`

---

¡Con estos pasos deberías poder hacer login y reset de contraseña sin problemas! 🎉
