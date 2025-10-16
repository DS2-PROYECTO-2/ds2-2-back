#!/usr/bin/env python3
"""
Script para validar la API key de Brevo
"""
import os
import requests
import sys

def validate_brevo_api_key():
    """Valida la API key de Brevo"""
    
    # Obtener API key de diferentes fuentes
    api_key = None
    
    # 1. Variable de entorno
    api_key = os.getenv('BREVO_API_KEY')
    if api_key:
        print(f"[INFO] API key encontrada en variable de entorno: {api_key[:10]}...")
    else:
        print("[WARNING] BREVO_API_KEY no encontrada en variables de entorno")
    
    # 2. Archivo .env local
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv('BREVO_API_KEY')
        if api_key:
            print(f"[INFO] API key encontrada en .env: {api_key[:10]}...")
    except ImportError:
        print("[WARNING] python-dotenv no instalado, saltando .env")
    except Exception as e:
        print(f"[WARNING] Error cargando .env: {e}")
    
    if not api_key:
        print("[ERROR] No se encontró BREVO_API_KEY en ninguna fuente")
        return False
    
    # Validar formato de API key
    if not api_key.startswith('xkeysib-'):
        print(f"[ERROR] Formato de API key inválido. Debe empezar con 'xkeysib-', encontrado: {api_key[:10]}...")
        return False
    
    if len(api_key) < 50:
        print(f"[ERROR] API key muy corta. Longitud: {len(api_key)}")
        return False
    
    print(f"[INFO] Formato de API key válido: {api_key[:10]}... (longitud: {len(api_key)})")
    
    # Probar API key con Brevo
    print("[INFO] Probando API key con Brevo API...")
    
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }
    
    # Endpoint para obtener información de la cuenta
    test_url = "https://api.brevo.com/v3/account"
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        
        print(f"[INFO] Status Code: {response.status_code}")
        print(f"[INFO] Response: {response.text}")
        
        if response.status_code == 200:
            print("[SUCCESS] ✅ API key válida y funcionando")
            return True
        elif response.status_code == 401:
            print("[ERROR] ❌ API key inválida o expirada")
            return False
        else:
            print(f"[WARNING] ⚠️ Respuesta inesperada: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] ❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Validando API key de Brevo...")
    print("=" * 50)
    
    success = validate_brevo_api_key()
    
    print("=" * 50)
    if success:
        print("✅ Validación exitosa")
        sys.exit(0)
    else:
        print("❌ Validación fallida")
        sys.exit(1)
