# scripts

Colección de utilidades y comprobaciones manuales del proyecto. No forman parte de la aplicación ni de la suite de tests automatizados.

- check_*.py: scripts de verificación puntual de base de datos/tablas/datos.
- debug_*.py: apoyo para depuración manual de flujos (duraciones, notificaciones, etc.).
- fix_notification_table.py: utilidades de mantenimiento/corrección rápida.
- show_urls.py: inspección de rutas.
- email_config.py, verify_email_config.py: pruebas de configuración de correo.

Ejecución (ejemplos):

```
# Desde la raíz del repo
.venv\\Scripts\\python.exe scripts\\check_database.py
.venv\\Scripts\\python.exe scripts\\debug_excessive_hours.py
```

Notas
- La carpeta scripts/ está excluida de la recolección de pytest (ver pytest.ini).
- No modificar datos de producción con estos scripts a menos que sepas exactamente qué haces.
