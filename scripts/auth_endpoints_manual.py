#!/usr/bin/env python3
"""
Script manual para probar los endpoints de autenticación
No es un test automatizado; se omite en pytest.
"""

import pytest
import requests
import json

# Omitir TODO el archivo en pytest
pytestmark = pytest.mark.skip(reason="Script manual; no forma parte de la suite de tests.")

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/auth"

def test_endpoint(method, url, data=None, headers=None):
    """Probar un endpoint y mostrar resultado"""
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == 'PATCH':
            response = requests.patch(url, json=data, headers=headers)
        
        print(f"\n🔍 {method} {url}")
        print(f"Status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        except ValueError:
            print(f"Response: {response.text}")
        
        return response
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: No se puede conectar a {url}")
        print("   Asegúrate de que el servidor Django esté ejecutándose")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

@pytest.mark.skip(reason="Script manual para probar endpoints en servidor; se omite en pytest.")
def main():
    print("🚀 Probando endpoints de autenticación")
    print("=" * 50)
    
    # 1. Probar registro de usuario
    print("\n1️⃣ Probando registro de usuario...")
    register_data = {
        "username": "test_user",
        "email": "test@ejemplo.com",
        "password": "test123456",
        "password_confirm": "test123456",
        "first_name": "Usuario",
        "last_name": "Prueba",
        "identification": "12345678",
        "phone": "3001234567",
        "role": "monitor"
    }
    
    test_endpoint('POST', f"{API_BASE}/register/", register_data)
    
    # 2. Probar login
    print("\n2️⃣ Probando login...")
    login_data = {
        "username": "test_user",
        "password": "test123456"
    }
    
    login_response = test_endpoint('POST', f"{API_BASE}/login/", login_data)
    
    # Extraer token si el login fue exitoso
    token = None
    if login_response and login_response.status_code == 200:
        try:
            response_data = login_response.json()
            token = response_data.get('token')
            print(f"✅ Token obtenido: {token[:20]}...")
        except ValueError:
            pass
    
    # 3. Probar perfil (requiere autenticación)
    if token:
        print("\n3️⃣ Probando perfil de usuario...")
        headers = {"Authorization": f"Token {token}"}
        test_endpoint('GET', f"{API_BASE}/profile/", headers=headers)
    
    # 4. Probar solicitud de reset de contraseña
    print("\n4️⃣ Probando solicitud de reset de contraseña...")
    reset_request_data = {
        "email": "test@ejemplo.com"
    }
    test_endpoint('POST', f"{API_BASE}/password/reset-request/", reset_request_data)
    
    # 5. Probar dashboard
    if token:
        print("\n5️⃣ Probando dashboard...")
        headers = {"Authorization": f"Token {token}"}
        test_endpoint('GET', f"{API_BASE}/dashboard/", headers=headers)
    
    # 6. Probar logout
    if token:
        print("\n6️⃣ Probando logout...")
        headers = {"Authorization": f"Token {token}"}
        test_endpoint('POST', f"{API_BASE}/logout/", headers=headers)
    
    print("\n" + "=" * 50)
    print("✅ Pruebas completadas")
    print("\n💡 Consejos:")
    print("- Si hay errores de conexión, asegúrate de que el servidor esté ejecutándose")
    print("- Revisa la consola del servidor para ver los emails (modo desarrollo)")
    print("- Los usuarios se crean en la base de datos")

if __name__ == "__main__":
    main()
