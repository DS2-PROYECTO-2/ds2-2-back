# Configuración de CI/CD

## Variables de Entorno Requeridas

Para que el despliegue automático funcione, necesitas configurar las siguientes variables de entorno en GitHub Secrets:

### 1. Ir a GitHub Repository Settings
- Ve a tu repositorio en GitHub
- Click en "Settings" → "Secrets and variables" → "Actions"

### 2. Agregar los siguientes secrets:

#### Para Render.com:
```
RENDER_SERVICE_ID=tu_service_id_aqui
RENDER_API_KEY=tu_api_key_aqui
RENDER_SERVICE_URL=https://tu-servicio.onrender.com
```

### 3. Cómo obtener estos valores:

#### RENDER_SERVICE_ID:
1. Ve a tu dashboard de Render.com
2. Selecciona tu servicio
3. En la URL del servicio, copia el ID (ejemplo: `srv-abc123def456`)

#### RENDER_API_KEY:
1. Ve a tu cuenta de Render.com
2. Settings → API Keys
3. Genera una nueva API key
4. Copia la key generada

#### RENDER_SERVICE_URL:
1. Es la URL pública de tu servicio
2. Ejemplo: `https://backendpruebas-r4zu.onrender.com`

## Workflows Disponibles

### 1. CI/CD Completo (`ci-cd.yml`)
- Ejecuta tests automáticamente
- Despliega automáticamente en push a main/develop Y en pull requests
- Permite probar el despliegue antes de hacer merge

### 2. CI Separado (`ci.yml`)
- Solo ejecuta tests
- Se ejecuta en push y pull requests

### 3. Deploy Separado (`deploy.yml`)
- Solo despliegue
- Se ejecuta después de que CI sea exitoso

## Flujo de Trabajo

1. **Pull Request**: Ejecuta tests + despliegue automático (CI/CD)
2. **Push a main/develop**: Ejecuta tests + despliegue automático (CI/CD)

## Monitoreo

- Ve a "Actions" en tu repositorio de GitHub para ver el estado de los workflows
- Los deployments aparecerán en Render.com automáticamente
- Recibirás notificaciones si algo falla

## Troubleshooting

### Si el despliegue falla:
1. Verifica que las variables de entorno estén configuradas correctamente
2. Revisa los logs en GitHub Actions
3. Verifica que el servicio en Render.com esté activo

### Si los tests fallan:
1. Revisa los logs de los tests
2. Verifica que todas las dependencias estén en requirements.txt
3. Asegúrate de que la configuración de testing sea correcta
