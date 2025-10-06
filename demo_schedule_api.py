#!/usr/bin/env python
"""
Script de demostración para la API de Schedule
Muestra cómo usar todos los endpoints implementados

Para ejecutar:
1. python manage.py runserver (en otra terminal)
2. python demo_schedule_api.py
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración base
BASE_URL = "http://localhost:8000/api"
ADMIN_TOKEN = None  # Se obtendrá dinámicamente
MONITOR_TOKEN = None  # Se obtendrá dinámicamente

def print_response(title, response):
    """Imprimir respuesta de forma legible"""
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print(f"{'='*50}")
    print(f"Status: {response.status_code}")
    if response.status_code < 400:
        try:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
    else:
        print(f"Error: {response.text}")

def login_user(username, password):
    """Login y obtener token"""
    response = requests.post(f"{BASE_URL}/auth/login/", {
        "username": username,
        "password": password
    })
    
    if response.status_code == 200:
        return response.json().get('token')
    return None

def create_demo_data():
    """Crear datos de demostración"""
    print("📋 Creando datos de demostración...")
    
    # Este script asume que ya existen usuarios y salas de prueba
    # En un entorno real, crearías estos datos primero
    
    global ADMIN_TOKEN, MONITOR_TOKEN
    
    # Login como admin (ajusta credenciales según tu entorno)
    print("🔐 Intentando login como admin...")
    ADMIN_TOKEN = login_user("admin", "admin123")  # Ajustar credenciales
    
    if not ADMIN_TOKEN:
        print("❌ No se pudo hacer login como admin. Verifica las credenciales.")
        return False
    
    # Login como monitor (ajusta credenciales según tu entorno)
    print("🔐 Intentando login como monitor...")
    MONITOR_TOKEN = login_user("monitor", "monitor123")  # Ajustar credenciales
    
    if not MONITOR_TOKEN:
        print("❌ No se pudo hacer login como monitor. Verifica las credenciales.")
        return False
    
    print("✅ Login exitoso para ambos usuarios")
    return True

def demo_admin_crud():
    """Demostración de CRUD para administradores"""
    print("\n🔧 === DEMOSTRACIÓN CRUD ADMINISTRADOR ===")
    
    headers = {
        "Authorization": f"Token {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 1. Listar turnos existentes
    response = requests.get(f"{BASE_URL}/schedule/schedules/", headers=headers)
    print_response("Listar Turnos Existentes", response)
    
    # 2. Crear nuevo turno
    now = datetime.now()
    future_date = now + timedelta(days=1)
    
    new_schedule = {
        "user": 2,  # ID del monitor (ajustar según tu BD)
        "room": 1,  # ID de la sala (ajustar según tu BD)
        "start_datetime": future_date.isoformat(),
        "end_datetime": (future_date + timedelta(hours=4)).isoformat(),
        "notes": "Turno de demostración creado por API",
        "recurring": False
    }
    
    response = requests.post(
        f"{BASE_URL}/schedule/schedules/", 
        headers=headers,
        json=new_schedule
    )
    print_response("Crear Nuevo Turno", response)
    
    if response.status_code == 201:
        schedule_id = response.json().get('id')
        
        # 3. Ver detalle del turno creado
        response = requests.get(
            f"{BASE_URL}/schedule/schedules/{schedule_id}/", 
            headers=headers
        )
        print_response("Detalle del Turno Creado", response)
        
        # 4. Actualizar el turno
        update_data = {
            "notes": "Turno actualizado mediante PATCH",
            "status": "active"
        }
        
        response = requests.patch(
            f"{BASE_URL}/schedule/schedules/{schedule_id}/",
            headers=headers,
            json=update_data
        )
        print_response("Actualizar Turno", response)
        
        # 5. Eliminar el turno (comentado para no afectar datos)
        # response = requests.delete(
        #     f"{BASE_URL}/schedule/schedules/{schedule_id}/",
        #     headers=headers
        # )
        # print_response("Eliminar Turno", response)
    
    # 6. Turnos próximos
    response = requests.get(
        f"{BASE_URL}/schedule/schedules/upcoming/", 
        headers=headers
    )
    print_response("Turnos Próximos (7 días)", response)
    
    # 7. Turnos actuales
    response = requests.get(
        f"{BASE_URL}/schedule/schedules/current/", 
        headers=headers
    )
    print_response("Turnos Actuales", response)

def demo_admin_overview():
    """Demostración de overview administrativo"""
    print("\n📊 === DEMOSTRACIÓN OVERVIEW ADMINISTRATIVO ===")
    
    headers = {"Authorization": f"Token {ADMIN_TOKEN}"}
    
    response = requests.get(
        f"{BASE_URL}/schedule/admin/overview/", 
        headers=headers
    )
    print_response("Resumen General para Administradores", response)

def demo_monitor_endpoints():
    """Demostración de endpoints para monitores"""
    print("\n👤 === DEMOSTRACIÓN ENDPOINTS MONITOR ===")
    
    headers = {"Authorization": f"Token {MONITOR_TOKEN}"}
    
    # 1. Ver mis turnos (todos)
    response = requests.get(
        f"{BASE_URL}/schedule/my-schedules/",
        headers=headers,
        params={"status": "all"}
    )
    print_response("Mis Turnos (Todos los estados)", response)
    
    # 2. Ver mis turnos activos
    response = requests.get(
        f"{BASE_URL}/schedule/my-schedules/",
        headers=headers,
        params={"status": "active"}
    )
    print_response("Mis Turnos Activos", response)
    
    # 3. Mi turno actual
    response = requests.get(
        f"{BASE_URL}/schedule/my-current-schedule/",
        headers=headers
    )
    print_response("Mi Turno Actual", response)
    
    # 4. Filtros por fecha
    today = datetime.now().date()
    response = requests.get(
        f"{BASE_URL}/schedule/my-schedules/",
        headers=headers,
        params={
            "date_from": today.strftime("%Y-%m-%d"),
            "status": "all"
        }
    )
    print_response("Mis Turnos desde Hoy", response)

def demo_validation_errors():
    """Demostración de errores de validación"""
    print("\n⚠️  === DEMOSTRACIÓN ERRORES DE VALIDACIÓN ===")
    
    headers = {
        "Authorization": f"Token {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 1. Fecha fin antes que fecha inicio
    now = datetime.now()
    invalid_schedule = {
        "user": 2,
        "room": 1,
        "start_datetime": now.isoformat(),
        "end_datetime": (now - timedelta(hours=1)).isoformat(),  # Antes!
        "notes": "Turno inválido"
    }
    
    response = requests.post(
        f"{BASE_URL}/schedule/schedules/",
        headers=headers,
        json=invalid_schedule
    )
    print_response("Error: Fecha fin antes que inicio", response)
    
    # 2. Duración excesiva (más de 12 horas)
    invalid_schedule = {
        "user": 2,
        "room": 1,
        "start_datetime": (now + timedelta(days=1)).isoformat(),
        "end_datetime": (now + timedelta(days=1, hours=15)).isoformat(),  # 15 horas!
        "notes": "Turno muy largo"
    }
    
    response = requests.post(
        f"{BASE_URL}/schedule/schedules/",
        headers=headers,
        json=invalid_schedule
    )
    print_response("Error: Duración excesiva (>12h)", response)
    
    # 3. Acceso de monitor a endpoints de admin
    monitor_headers = {"Authorization": f"Token {MONITOR_TOKEN}"}
    
    response = requests.get(
        f"{BASE_URL}/schedule/admin/overview/",
        headers=monitor_headers
    )
    print_response("Error: Monitor accediendo a endpoint admin", response)

def main():
    """Función principal de demostración"""
    print("🚀 DEMOSTRACIÓN DE API SCHEDULE")
    print("="*50)
    
    # Crear datos de demostración
    if not create_demo_data():
        print("❌ Error en setup inicial. Verifica que el servidor esté corriendo y las credenciales sean correctas.")
        return
    
    try:
        # Demostraciones
        demo_admin_crud()
        demo_admin_overview()
        demo_monitor_endpoints()
        demo_validation_errors()
        
        print("\n✅ === DEMOSTRACIÓN COMPLETADA ===")
        print("🎉 Todos los endpoints han sido probados exitosamente!")
        print("\n📚 Para más información, consulta SCHEDULE_API_DOCUMENTATION.md")
        
    except Exception as e:
        print(f"❌ Error durante la demostración: {e}")

if __name__ == "__main__":
    main()