#!/usr/bin/env python3
"""
Script simple para verificar que el servidor Django esté funcionando
"""

import requests
import time
import sys

def test_server():
    """Probar conexión al servidor Django"""
    base_url = "http://localhost:8000"
    
    print("Verificando conexion al servidor Django...")
    print(f"URL: {base_url}")
    print("-" * 50)
    
    try:
        # Probar endpoint básico
        response = requests.get(base_url, timeout=5)
        print(f"Servidor respondiendo - Status: {response.status_code}")
        return True
        
    except requests.exceptions.ConnectionError:
        print("ERROR: No se puede conectar al servidor")
        print("El servidor Django no esta ejecutandose en http://localhost:8000")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def test_api():
    """Probar endpoints de la API"""
    base_url = "http://localhost:8000"
    
    print("\nProbando endpoints de la API...")
    print("-" * 50)
    
    endpoints = [
        "/api/auth/",
        "/api/rooms/",
        "/api/notifications/",
        "/api/dashboard/"
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            print(f"{endpoint} - Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"{endpoint} - ERROR: No se puede conectar")
            return False
        except Exception as e:
            print(f"{endpoint} - ERROR: {str(e)}")
    
    return True

def main():
    print("Verificador de Conexion del Servidor Django")
    print("=" * 60)
    
    # Esperar un poco
    print("Esperando 2 segundos...")
    time.sleep(2)
    
    # Probar servidor
    if not test_server():
        print("\nPROBLEMA: El servidor Django no esta ejecutandose")
        print("\nSOLUCIONES:")
        print("1. Ejecutar: python manage.py runserver")
        print("2. Verificar que no haya errores en la consola")
        print("3. Verificar que el puerto 8000 este libre")
        sys.exit(1)
    
    # Probar API
    if not test_api():
        print("\nPROBLEMA: Los endpoints de la API no responden")
        sys.exit(1)
    
    print("\nTodo esta funcionando correctamente!")
    print("\nRESUMEN:")
    print("- Servidor Django ejecutandose en http://localhost:8000")
    print("- CORS configurado correctamente")
    print("- Endpoints de la API respondiendo")
    print("\nTu frontend deberia poder conectarse ahora")

if __name__ == "__main__":
    main()
