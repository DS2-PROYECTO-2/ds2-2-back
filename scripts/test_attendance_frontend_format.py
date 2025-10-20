#!/usr/bin/env python
"""
Script para mostrar el formato correcto de petición para el frontend
"""
import requests
import tempfile
import os

def test_correct_format():
    """Mostrar el formato correcto de petición"""
    print("🔍 Formato correcto para subir listados de asistencia")
    print("=" * 60)
    
    # Crear archivo de prueba
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Listado de Asistencia de Prueba\n")
        f.write("Fecha: 2025-01-20\n")
        f.write("Monitor 1: Presente\n")
        f.write("Monitor 2: Ausente\n")
        f.write("Monitor 3: Presente\n")
        test_file_path = f.name
    
    try:
        # Token de ejemplo (reemplazar con token real)
        token = "tu_token_aqui"
        headers = {"Authorization": f"Token {token}"}
        
        print("📤 FORMATO CORRECTO (multipart/form-data):")
        print("-" * 40)
        
        # Método 1: Usando requests con files
        print("1. Usando requests (Python):")
        print("""
import requests

headers = {
    'Authorization': 'Token tu_token_aqui'
}

# Crear FormData
files = {'file': ('listado.txt', open('archivo.txt', 'rb'), 'text/plain')}
data = {
    'title': 'Listado de Asistencia - Enero 2025',
    'date': '2025-01-20',
    'description': 'Listado de asistencia del mes de enero'
}

response = requests.post(
    'http://127.0.0.1:8000/api/attendance/attendances/',
    headers=headers,
    files=files,
    data=data
)
        """)
        
        print("\n2. Usando fetch (JavaScript):")
        print("""
// Crear FormData
const formData = new FormData();
formData.append('title', 'Listado de Asistencia - Enero 2025');
formData.append('date', '2025-01-20');
formData.append('file', fileInput.files[0]); // Archivo del input
formData.append('description', 'Listado de asistencia del mes de enero');

// Enviar petición
fetch('http://127.0.0.1:8000/api/attendance/attendances/', {
    method: 'POST',
    headers: {
        'Authorization': 'Token tu_token_aqui'
        // NO incluir Content-Type - se establece automáticamente
    },
    body: formData
})
.then(response => response.json())
.then(data => console.log('Listado subido:', data));
        """)
        
        print("\n3. Usando axios (JavaScript):")
        print("""
import axios from 'axios';

const formData = new FormData();
formData.append('title', 'Listado de Asistencia - Enero 2025');
formData.append('date', '2025-01-20');
formData.append('file', fileInput.files[0]);
formData.append('description', 'Listado de asistencia del mes de enero');

axios.post('http://127.0.0.1:8000/api/attendance/attendances/', formData, {
    headers: {
        'Authorization': 'Token tu_token_aqui',
        'Content-Type': 'multipart/form-data'
    }
})
.then(response => console.log('Listado subido:', response.data));
        """)
        
        print("\n❌ FORMATO INCORRECTO (JSON):")
        print("-" * 40)
        print("""
// ❌ INCORRECTO - No funciona para archivos
fetch('http://127.0.0.1:8000/api/attendance/attendances/', {
    method: 'POST',
    headers: {
        'Authorization': 'Token tu_token_aqui',
        'Content-Type': 'application/json'  // ❌ INCORRECTO
    },
    body: JSON.stringify({  // ❌ INCORRECTO
        title: 'Listado de Asistencia',
        date: '2025-01-20',
        file: 'archivo.txt',  // ❌ No se puede enviar archivo como string
        description: 'Descripción'
    })
})
        """)
        
        print("\n🔧 SOLUCIÓN PARA EL FRONTEND:")
        print("-" * 40)
        print("1. Usar FormData en lugar de JSON")
        print("2. NO establecer Content-Type manualmente")
        print("3. Incluir el archivo real en el FormData")
        print("4. Enviar como multipart/form-data")
        
        print("\n📋 CAMPOS REQUERIDOS:")
        print("- title: string (requerido)")
        print("- date: string en formato YYYY-MM-DD (requerido)")
        print("- file: File object (requerido)")
        print("- description: string (opcional)")
        
    finally:
        # Limpiar archivo temporal
        os.unlink(test_file_path)

def test_actual_request():
    """Probar petición real"""
    print("\n🧪 Probando petición real...")
    
    # Crear archivo de prueba
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Listado de Asistencia de Prueba\n")
        f.write("Fecha: 2025-01-20\n")
        f.write("Monitor 1: Presente\n")
        f.write("Monitor 2: Ausente\n")
        f.write("Monitor 3: Presente\n")
        test_file_path = f.name
    
    try:
        # Token de ejemplo (reemplazar con token real)
        token = "tu_token_aqui"
        headers = {"Authorization": f"Token {token}"}
        
        # Preparar FormData
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_attendance.txt', f, 'text/plain')}
            data = {
                'title': 'Listado de Asistencia - Prueba Frontend',
                'date': '2025-01-20',
                'description': 'Listado de prueba para frontend'
            }
            
            print("📤 Enviando petición...")
            response = requests.post(
                'http://127.0.0.1:8000/api/attendance/attendances/',
                headers=headers,
                files=files,
                data=data
            )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Petición exitosa!")
        else:
            print("❌ Error en petición")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Limpiar archivo temporal
        os.unlink(test_file_path)

if __name__ == "__main__":
    test_correct_format()
    test_actual_request()
