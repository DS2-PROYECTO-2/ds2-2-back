#!/usr/bin/env python3
"""
Script para probar el restablecimiento de contraseña
"""

import requests
import json

def test_password_reset():
    """Probar el flujo completo de restablecimiento de contraseña"""
    base_url = "http://localhost:8000"
    
    print("Probando restablecimiento de contraseña...")
    print("=" * 60)
    
    # 1. Solicitar restablecimiento
    print("1. SOLICITAR RESTABLECIMIENTO")
    reset_data = {"email": "admin@example.com"}
    
    try:
        response = requests.post(f"{base_url}/api/auth/password/reset-request/", json=reset_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if 'reset_url' in data:
                reset_url = data['reset_url']
                print(f"\n   ENLACE DE DESARROLLO:")
                print(f"   {reset_url}")
                print(f"\n   Copia y pega este enlace en tu navegador para continuar")
                
                # Extraer token del URL
                if 'token=' in reset_url:
                    token = reset_url.split('token=')[1]
                    print(f"\n   TOKEN EXTRAÍDO: {token}")
                    
                    # 2. Validar token
                    print("\n2. VALIDAR TOKEN")
                    try:
                        validate_response = requests.get(f"{base_url}/api/auth/password/reset-confirm/?token={token}")
                        print(f"   Status: {validate_response.status_code}")
                        print(f"   Response: {validate_response.json()}")
                        
                        if validate_response.status_code == 200:
                            # 3. Confirmar nueva contraseña
                            print("\n3. CONFIRMAR NUEVA CONTRASEÑA")
                            confirm_data = {
                                "token": token,
                                "new_password": "nuevapassword123",
                                "new_password_confirm": "nuevapassword123"
                            }
                            
                            try:
                                confirm_response = requests.post(f"{base_url}/api/auth/password/reset-confirm/", json=confirm_data)
                                print(f"   Status: {confirm_response.status_code}")
                                print(f"   Response: {confirm_response.json()}")
                                
                                if confirm_response.status_code == 200:
                                    print("\n   ✅ CONTRASEÑA RESTABLECIDA EXITOSAMENTE")
                                else:
                                    print(f"\n   ❌ ERROR AL CONFIRMAR: {confirm_response.text}")
                            except Exception as e:
                                print(f"   ERROR: {e}")
                        else:
                            print(f"\n   ❌ ERROR AL VALIDAR TOKEN: {validate_response.text}")
                    except Exception as e:
                        print(f"   ERROR: {e}")
            else:
                print("   No se devolvió enlace de desarrollo")
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("RESUMEN:")
    print("1. El email se envía a la consola del servidor")
    print("2. En desarrollo, el enlace se devuelve en la respuesta")
    print("3. Puedes copiar y pegar el enlace en el navegador")
    print("4. El token expira en 2 horas")

def main():
    test_password_reset()

if __name__ == "__main__":
    main()
