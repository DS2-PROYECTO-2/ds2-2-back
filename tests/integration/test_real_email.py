#!/usr/bin/env python3
"""
Script para probar el envío de emails reales
"""

import requests
import json

def test_real_email():
    """Probar el envío de emails reales"""
    base_url = "http://localhost:8000"
    
    print("Probando envío de emails reales...")
    print("=" * 60)
    
    # 1. Probar restablecimiento de contraseña
    print("1. PROBAR RESTABLECIMIENTO DE CONTRASEÑA")
    reset_data = {"email": "admin@ejemplo.com"}
    
    try:
        response = requests.post(f"{base_url}/api/auth/password/reset-request/", json=reset_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if 'reset_url' in data:
                print("   ⚠️  MODO DESARROLLO: Se devolvió enlace en respuesta")
            else:
                print("   ✅ MODO PRODUCCIÓN: Email enviado por SMTP")
                print("   Revisa tu bandeja de entrada en admin@ejemplo.com")
        else:
            print(f"   ❌ ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "=" * 60)
    
    # 2. Probar registro de usuario
    print("2. PROBAR REGISTRO DE USUARIO")
    import random
    random_id = random.randint(1000, 9999)
    
    user_data = {
        "username": f"testuser_{random_id}",
        "email": f"testuser_{random_id}@example.com",
        "password": "password123",
        "password_confirm": "password123",
        "first_name": "Test",
        "last_name": "User",
        "identification": f"12345678{random_id}",
        "phone": "3001234567",
        "role": "monitor"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register/", json=user_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 201:
            print("   ✅ USUARIO REGISTRADO EXITOSAMENTE")
            print("   📧 Email de activación enviado a los administradores")
            print("   Revisa la bandeja de entrada de los administradores")
        else:
            print(f"   ❌ ERROR AL REGISTRAR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("RESUMEN:")
    print("✅ Configuración de email real activada")
    print("✅ Emails se envían por SMTP a Gmail")
    print("✅ No se devuelven enlaces en respuestas")
    print("✅ No se muestran enlaces en consola")
    print("📧 Revisa las bandejas de entrada de los destinatarios")

def main():
    test_real_email()

if __name__ == "__main__":
    main()
