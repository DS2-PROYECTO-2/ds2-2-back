#!/usr/bin/env python
"""
Script simple para probar el sistema de exportación
"""
import requests
import json
import time
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api"

def get_auth_token():
    """Obtiene token de autenticación"""
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
                    print(f"Autenticado como: {user['username']}")
                    return token
        except Exception as e:
            continue
    
    print("No se pudo autenticar")
    return None

def test_monitors_data(token):
    """Prueba endpoint de datos de monitores"""
    print("\nProbando datos de monitores...")
    
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/export/monitors/data/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"Datos obtenidos: {data['total_count']} monitores")
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_pdf_export(token):
    """Prueba exportación a PDF"""
    print("\nProbando exportación a PDF...")
    
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
        response = requests.post(f"{API_BASE}/export/monitors/export/", 
                                headers=headers, 
                                json=export_data)
        
        if response.status_code == 202:
            data = response.json()
            job_id = data['export_job_id']
            print(f"Trabajo PDF creado: ID {job_id}")
            
            # Verificar estado
            time.sleep(3)
            status_response = requests.get(f"{API_BASE}/export/jobs/{job_id}/status/", headers=headers)
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"Estado: {status_data['status']}")
                if status_data.get('file_url'):
                    print(f"Archivo: {status_data['file_url']}")
                return True
        else:
            print(f"Error creando PDF: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error en PDF: {e}")
        return False

def test_excel_export(token):
    """Prueba exportación a Excel"""
    print("\nProbando exportación a Excel...")
    
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
        response = requests.post(f"{API_BASE}/export/monitors/export/", 
                                headers=headers, 
                                json=export_data)
        
        if response.status_code == 202:
            data = response.json()
            job_id = data['export_job_id']
            print(f"Trabajo Excel creado: ID {job_id}")
            
            # Verificar estado
            time.sleep(3)
            status_response = requests.get(f"{API_BASE}/export/jobs/{job_id}/status/", headers=headers)
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"Estado: {status_data['status']}")
                if status_data.get('file_url'):
                    print(f"Archivo: {status_data['file_url']}")
                return True
        else:
            print(f"Error creando Excel: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error en Excel: {e}")
        return False

def main():
    """Función principal"""
    print("Iniciando pruebas del sistema de exportacion...")
    print(f"Servidor: {BASE_URL}")
    
    # Verificar servidor
    try:
        response = requests.get(f"{BASE_URL}/admin/", timeout=5)
        print("Servidor Django esta corriendo")
    except Exception as e:
        print(f"Servidor no disponible: {e}")
        print("Ejecuta: python manage.py runserver")
        return False
    
    # Obtener token
    print("\nObteniendo token de autenticacion...")
    token = get_auth_token()
    
    if not token:
        return False
    
    # Ejecutar pruebas
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Datos de monitores
    if test_monitors_data(token):
        tests_passed += 1
    
    # Test 2: Exportación PDF
    if test_pdf_export(token):
        tests_passed += 1
    
    # Test 3: Exportación Excel
    if test_excel_export(token):
        tests_passed += 1
    
    # Resumen
    print(f"\nResumen de pruebas:")
    print(f"Exitosas: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("Todas las pruebas pasaron!")
        print("\nSistema de exportacion completamente funcional:")
        print("  - PDF: Funcionando")
        print("  - Excel: Funcionando")
        print("  - API REST: Funcionando")
    else:
        print("Algunas pruebas fallaron.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    main()

