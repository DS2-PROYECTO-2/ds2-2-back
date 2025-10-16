#!/usr/bin/env python3
"""
Script para configurar la API key de Brevo en diferentes entornos
"""
import os
import sys

def setup_brevo_key():
    """Configura la API key de Brevo"""
    
    print("Configurando API key de Brevo...")
    print("=" * 50)
    
    # API key proporcionada por el usuario
    api_key = "[CONFIGURAR_BREVO_API_KEY_AQUI]"
    
    print(f"[INFO] API key: {api_key}")
    
    # 1. Verificar si ya está configurada
    current_key = os.getenv('BREVO_API_KEY')
    if current_key:
        print(f"[INFO] API key actual: {current_key[:10]}...")
        if current_key == api_key:
            print("[SUCCESS] API key ya está configurada correctamente")
            return True
        else:
            print("[WARNING] API key diferente encontrada")
    
    # 2. Configurar para desarrollo local
    print("\n[INFO] Configurando para desarrollo local...")
    
    # Crear/actualizar .env
    env_file = ".env"
    env_content = []
    
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_content = f.readlines()
    
    # Buscar y actualizar BREVO_API_KEY
    updated = False
    for i, line in enumerate(env_content):
        if line.startswith('BREVO_API_KEY='):
            env_content[i] = f'BREVO_API_KEY={api_key}\n'
            updated = True
            break
    
    if not updated:
        env_content.append(f'BREVO_API_KEY={api_key}\n')
    
    # Escribir archivo .env
    with open(env_file, 'w') as f:
        f.writelines(env_content)
    
    print(f"[SUCCESS] API key configurada en {env_file}")
    
    # 3. Mostrar instrucciones para otros entornos
    print("\n[INFO] Instrucciones para otros entornos:")
    print("=" * 50)
    
    print("\nGitHub Secrets:")
    print("1. Ve a tu repositorio en GitHub")
    print("2. Settings > Secrets and variables > Actions")
    print("3. New repository secret")
    print("4. Name: BREVO_API_KEY")
    print("5. Value: [TU_BREVO_API_KEY_AQUI]")
    
    print("\nRender Dashboard:")
    print("1. Ve a tu servicio en Render Dashboard")
    print("2. Environment > Add Environment Variable")
    print("3. Key: BREVO_API_KEY")
    print("4. Value: [TU_BREVO_API_KEY_AQUI]")
    
    print("\nCI/CD (GitHub Actions):")
    print("El workflow ya está configurado para usar GitHub Secrets")
    
    return True

if __name__ == "__main__":
    success = setup_brevo_key()
    
    if success:
        print("\nConfiguración completada")
        print("\nPróximos pasos:")
        print("1. Configura la API key en GitHub Secrets")
        print("2. Configura la API key en Render Dashboard")
        print("3. Ejecuta: python scripts/validate_brevo_key.py")
        print("4. Haz commit y push para probar en CI/CD")
    else:
        print("\nError en la configuración")
        sys.exit(1)
