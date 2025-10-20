#!/usr/bin/env python
"""
Script completo para probar el sistema de exportación
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
    # Intentar diferentes usuarios de prueba
    test_users = [
        {"username": "admin", "password": "admin123"},
        {"username": "monitor1", "password": "monitor123"},
        {"username": "test", "password": "test123"}
    ]
    
    for user in test_users:
        try:
            response = requests.post(f"{API_BASE}/auth/login/", json=user)
            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                if token:
                    print(f"✅ Autenticado como: {user['username']}")
                    return token
        except Exception as e:
            continue
    
    print("❌ No se pudo autenticar con ningún usuario de prueba")
    print("💡 Asegúrate de que el servidor esté corriendo y que existan usuarios")
    return None

def test_basic_endpoints(token):
    """Prueba endpoints básicos de datos"""
    print("\n🔍 Probando endpoints de datos...")
    
    headers = {"Authorization": f"Token {token}"}
    endpoints = [
        ("/export/monitors/data/", "Datos de monitores"),
        ("/export/room-entries/data/", "Entradas a salas"),
        ("/export/schedules/data/", "Turnos")
    ]
    
    success_count = 0
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                count = data.get('total_count', 0)
                print(f"✅ {name}: {count} registros")
                success_count += 1
            else:
                print(f"❌ {name}: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    return success_count == len(endpoints)

def test_pdf_export(token):
    """Prueba exportación a PDF"""
    print("\n📄 Probando exportación a PDF...")
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    export_data = {
        "export_type": "monitors_data",
        "format": "pdf",
        "title": f"Prueba PDF - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    }
    
    try:
        # Crear trabajo de exportación
        response = requests.post(f"{API_BASE}/export/monitors/export/", 
                                headers=headers, 
                                json=export_data)
        
        if response.status_code == 202:
            data = response.json()
            job_id = data['export_job_id']
            print(f"✅ Trabajo PDF creado: ID {job_id}")
            
            # Monitorear progreso
            return monitor_export_progress(token, job_id, "PDF")
        else:
            print(f"❌ Error creando PDF: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en PDF: {e}")
        return False

def test_excel_export(token):
    """Prueba exportación a Excel"""
    print("\n📊 Probando exportación a Excel...")
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    export_data = {
        "export_type": "monitors_data",
        "format": "excel",
        "title": f"Prueba Excel - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    }
    
    try:
        # Crear trabajo de exportación
        response = requests.post(f"{API_BASE}/export/monitors/export/", 
                                headers=headers, 
                                json=export_data)
        
        if response.status_code == 202:
            data = response.json()
            job_id = data['export_job_id']
            print(f"✅ Trabajo Excel creado: ID {job_id}")
            
            # Monitorear progreso
            return monitor_export_progress(token, job_id, "Excel")
        else:
            print(f"❌ Error creando Excel: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en Excel: {e}")
        return False

def monitor_export_progress(token, job_id, format_name):
    """Monitorea el progreso de una exportación"""
    headers = {"Authorization": f"Token {token}"}
    
    print(f"⏳ Monitoreando progreso de {format_name}...")
    
    for attempt in range(10):  # Máximo 10 intentos (20 segundos)
        try:
            response = requests.get(f"{API_BASE}/export/jobs/{job_id}/status/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                status = data['status']
                print(f"📊 Estado: {status}")
                
                if status == 'completed':
                    file_url = data.get('file_url')
                    file_size = data.get('file_size_mb')
                    print(f"✅ {format_name} completado!")
                    print(f"📁 Archivo: {file_url}")
                    print(f"📏 Tamaño: {file_size} MB")
                    return True
                elif status == 'failed':
                    error = data.get('error_message', 'Error desconocido')
                    print(f"❌ {format_name} falló: {error}")
                    return False
                else:
                    time.sleep(2)  # Esperar 2 segundos antes del siguiente intento
            else:
                print(f"❌ Error verificando estado: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error monitoreando: {e}")
            return False
    
    print(f"⏰ Timeout esperando {format_name}")
    return False

def test_filtered_export(token):
    """Prueba exportación con filtros"""
    print("\n🔍 Probando exportación con filtros...")
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    # Exportar con filtros de fecha
    export_data = {
        "export_type": "monitors_data",
        "format": "pdf",
        "title": f"Prueba con Filtros - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
    
    try:
        response = requests.post(f"{API_BASE}/export/monitors/export/", 
                                headers=headers, 
                                json=export_data)
        
        if response.status_code == 202:
            data = response.json()
            job_id = data['export_job_id']
            print(f"✅ Trabajo con filtros creado: ID {job_id}")
            return True
        else:
            print(f"❌ Error con filtros: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error con filtros: {e}")
        return False

def test_download_file(token, job_id):
    """Prueba descarga de archivo"""
    print(f"\n📥 Probando descarga de archivo {job_id}...")
    
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/export/jobs/{job_id}/download/", headers=headers)
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            content_length = response.headers.get('content-length', '0')
            
            print(f"✅ Archivo descargado!")
            print(f"📄 Tipo: {content_type}")
            print(f"📏 Tamaño: {int(content_length) / 1024:.1f} KB")
            return True
        else:
            print(f"❌ Error descargando: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error descargando: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🧪 Iniciando pruebas completas del sistema de exportación...")
    print(f"🌐 Servidor: {BASE_URL}")
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/admin/", timeout=5)
        print("✅ Servidor Django está corriendo")
    except Exception as e:
        print(f"❌ Servidor no disponible: {e}")
        print("💡 Asegúrate de ejecutar: python manage.py runserver")
        return False
    
    # Obtener token de autenticación
    print("\n🔐 Obteniendo token de autenticación...")
    token = get_auth_token()
    
    if not token:
        return False
    
    # Ejecutar pruebas
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Endpoints básicos
    if test_basic_endpoints(token):
        tests_passed += 1
    
    # Test 2: Exportación PDF
    if test_pdf_export(token):
        tests_passed += 1
    
    # Test 3: Exportación Excel
    if test_excel_export(token):
        tests_passed += 1
    
    # Test 4: Exportación con filtros
    if test_filtered_export(token):
        tests_passed += 1
    
    # Test 5: Listar trabajos
    try:
        headers = {"Authorization": f"Token {token}"}
        response = requests.get(f"{API_BASE}/export/jobs/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"\n📋 Trabajos de exportación: {count}")
            tests_passed += 1
        else:
            print(f"❌ Error listando trabajos: {response.status_code}")
    except Exception as e:
        print(f"❌ Error listando trabajos: {e}")
    
    # Resumen final
    print(f"\n📊 Resumen de pruebas:")
    print(f"✅ Exitosas: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 ¡Todas las pruebas pasaron!")
        print("\n🚀 Sistema de exportación completamente funcional:")
        print("   • PDF: ✅ Funcionando")
        print("   • Excel: ✅ Funcionando")
        print("   • Filtros: ✅ Funcionando")
        print("   • API REST: ✅ Funcionando")
        print("\n📝 Endpoints disponibles:")
        print(f"   • {API_BASE}/export/monitors/export/")
        print(f"   • {API_BASE}/export/monitors/data/")
        print(f"   • {API_BASE}/export/room-entries/data/")
        print(f"   • {API_BASE}/export/schedules/data/")
        print(f"   • {API_BASE}/export/jobs/")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    main()

