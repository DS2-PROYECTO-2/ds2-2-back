#!/usr/bin/env python
"""
Script para probar los endpoints de exportación
"""
import requests
import json
import time
import os
from datetime import datetime, date

# Configuración
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api"

def get_auth_token():
    """Obtiene token de autenticación"""
    # Datos de prueba - ajustar según tu configuración
    login_data = {
        "username": "admin",  # Cambiar por usuario válido
        "password": "admin123"  # Cambiar por contraseña válida
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login/", json=login_data)
        if response.status_code == 200:
            data = response.json()
            return data.get('token')
        else:
            print(f"❌ Error en login: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return None

def test_monitors_data(token):
    """Prueba el endpoint de datos de monitores"""
    print("\n🔍 Probando endpoint de datos de monitores...")
    
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/export/monitors/data/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Datos obtenidos: {data['total_count']} monitores")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_export_job(token):
    """Prueba crear un trabajo de exportación"""
    print("\n📤 Probando creación de trabajo de exportación...")
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    export_data = {
        "export_type": "monitors_data",
        "format": "pdf",
        "title": f"Prueba de Exportación - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
    
    try:
        response = requests.post(f"{API_BASE}/export/monitors/export/", 
                                headers=headers, 
                                json=export_data)
        
        if response.status_code == 202:
            data = response.json()
            print(f"✅ Trabajo creado: ID {data['export_job_id']}")
            return data['export_job_id']
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_export_status(token, job_id):
    """Verifica el estado de un trabajo de exportación"""
    print(f"\n⏳ Verificando estado del trabajo {job_id}...")
    
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/export/jobs/{job_id}/status/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Estado: {data['status']}")
            if data.get('file_url'):
                print(f"📁 Archivo: {data['file_url']}")
            if data.get('error_message'):
                print(f"⚠️  Error: {data['error_message']}")
            return data['status']
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_room_entries_data(token):
    """Prueba el endpoint de datos de entradas a salas"""
    print("\n🏠 Probando endpoint de entradas a salas...")
    
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/export/room-entries/data/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Datos obtenidos: {data['total_count']} entradas")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_schedules_data(token):
    """Prueba el endpoint de datos de turnos"""
    print("\n📅 Probando endpoint de turnos...")
    
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/export/schedules/data/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Datos obtenidos: {data['total_count']} turnos")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🧪 Iniciando pruebas de endpoints de exportación...")
    print(f"🌐 Servidor: {BASE_URL}")
    
    # Obtener token de autenticación
    print("\n🔐 Obteniendo token de autenticación...")
    token = get_auth_token()
    
    if not token:
        print("❌ No se pudo obtener token. Verifica las credenciales y que el servidor esté corriendo.")
        return False
    
    print("✅ Token obtenido correctamente")
    
    # Ejecutar pruebas
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Datos de monitores
    if test_monitors_data(token):
        tests_passed += 1
    
    # Test 2: Entradas a salas
    if test_room_entries_data(token):
        tests_passed += 1
    
    # Test 3: Turnos
    if test_schedules_data(token):
        tests_passed += 1
    
    # Test 4: Crear trabajo de exportación
    job_id = test_export_job(token)
    if job_id:
        tests_passed += 1
        
        # Verificar estado del trabajo
        time.sleep(2)  # Esperar un poco
        status = check_export_status(token, job_id)
        if status:
            print(f"📊 Estado final: {status}")
    
    # Resumen
    print(f"\n📊 Resumen de pruebas:")
    print(f"✅ Exitosas: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 ¡Todas las pruebas pasaron!")
        print("\n📝 Endpoints funcionando correctamente:")
        print(f"   • {API_BASE}/export/monitors/data/")
        print(f"   • {API_BASE}/export/room-entries/data/")
        print(f"   • {API_BASE}/export/schedules/data/")
        print(f"   • {API_BASE}/export/monitors/export/")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    main()

