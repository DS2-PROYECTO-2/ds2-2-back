# 🔧 Configuración de Brevo API

## **📋 Pasos para Configurar BREVO_API_KEY**

### **1. GitHub Repository Secrets**
1. Ve a tu repositorio en GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. **Name:** `BREVO_API_KEY`
5. **Value:** `[TU_BREVO_API_KEY_AQUI]`

### **2. Render Dashboard**
1. Ve a tu servicio en Render Dashboard
2. **Environment** → **Add Environment Variable**
3. **Key:** `BREVO_API_KEY`
4. **Value:** `[TU_BREVO_API_KEY_AQUI]`

### **3. Desarrollo Local**
Agregar a tu archivo `.env`:
```
BREVO_API_KEY=[TU_BREVO_API_KEY_AQUI]
```

## **✅ Verificación**

### **Tests Locales:**
```bash
python manage.py test --settings=ds2_back.settings.testing
```

### **Tests en CI:**
Los tests usarán automáticamente la API key de GitHub Secrets.

### **Producción:**
Render usará la variable de entorno configurada en el Dashboard.

## **🔍 Logs de Debug**

Los logs mostrarán:
- `[BREVO_DEBUG]` - Información de configuración
- `[BREVO_TEST]` - Simulación en tests
- `[BREVO_ERROR]` - Errores de API
- `[EMAIL_SUCCESS]` - Envío exitoso

## **📧 Funcionamiento**

1. **Tests:** Simula envío sin API real
2. **Desarrollo:** Usa API key local
3. **Producción:** Usa API key de Render
4. **CI/CD:** Usa API key de GitHub Secrets
