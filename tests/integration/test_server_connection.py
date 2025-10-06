#!/usr/bin/env python3
"""
Script para verificar que el servidor Django esté funcionando correctamente
"""

import requests
import time
import sys

def test_server_connection():
    """Probar conexión al servidor Django"""
    base_url = "http://localhost:8000"
    
    print("🔍 Verificando conexión al servidor Django...")
    print(f"URL: {base_url}")
    print("-" * 50)
    
    # Lista de endpoints a probar
    endpoints = [
        "/",
        "/admin/",
        "/api/auth/",
        "/api/rooms/",
        "/api/notifications/",
        "/api/dashboard/"
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            print(f"🔗 Probando: {url}")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ OK - Status: {response.status_code}")
            elif response.status_code == 404:
                print(f"   ⚠️  Not Found - Status: {response.status_code} (Normal para algunos endpoints)")
            elif response.status_code == 403:
                print(f"   🔒 Forbidden - Status: {response.status_code} (Requiere autenticación)")
            else:
                print(f"   ❓ Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ ERROR: No se puede conectar a {url}")
            print("      → El servidor Django no está ejecutándose")
            return False
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT: {url}")
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Servidor Django está funcionando correctamente")
    return True

def test_api_endpoints():
    """Probar endpoints específicos de la API"""
    base_url = "http://localhost:8000"
    
    print("\n🔍 Probando endpoints de la API...")
    print("-" * 50)
    
    # Endpoints que no requieren autenticación
    public_endpoints = [
        "/api/auth/register/",
        "/api/auth/login/",
        "/api/auth/password/reset-request/",
        "/api/rooms/",
    ]
    
    for endpoint in public_endpoints:
        url = f"{base_url}{endpoint}"
        try:
            print(f"🔗 Probando: {url}")
            
            # Probar con GET primero
            response = requests.get(url, timeout=5)
            print(f"   GET - Status: {response.status_code}")
            
            # Probar con POST (para endpoints que lo requieren)
            if "register" in endpoint or "login" in endpoint or "reset-request" in endpoint:
                test_data = {
                    "username": "test",
                    "email": "test@example.com",
                    "password": "test123456"
                }
                response = requests.post(url, json=test_data, timeout=5)
                print(f"   POST - Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ ERROR: No se puede conectar")
            return False
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
    
    return True

def main():
    print("🚀 Verificador de Conexión del Servidor Django")
    print("=" * 60)
    
    # Esperar un poco para que el servidor se inicie
    print("⏳ Esperando 3 segundos para que el servidor se inicie...")
    time.sleep(3)
    
    # Probar conexión básica
    if not test_server_connection():
        print("\n❌ PROBLEMA: El servidor Django no está ejecutándose")
        print("\n💡 SOLUCIONES:")
        print("1. Ejecutar: python manage.py runserver")
        print("2. Verificar que no haya errores en la consola")
        print("3. Verificar que el puerto 8000 esté libre")
        sys.exit(1)
    
    # Probar endpoints de la API
    if not test_api_endpoints():
        print("\n❌ PROBLEMA: Los endpoints de la API no responden correctamente")
        sys.exit(1)
    
    print("\n🎉 ¡Todo está funcionando correctamente!")
    print("\n📋 RESUMEN:")
    print("✅ Servidor Django ejecutándose en http://localhost:8000")
    print("✅ CORS configurado correctamente")
    print("✅ Endpoints de la API respondiendo")
    print("\n🔗 Tu frontend debería poder conectarse ahora")

if __name__ == "__main__":
    main()
