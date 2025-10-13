#!/usr/bin/env python3
"""
Script para corregir problemas de zona horaria en el código
"""

import os
import re

def fix_timezone_issues():
    """Corrige problemas de zona horaria en los archivos del proyecto"""
    
    # Archivos a corregir
    files_to_fix = [
        'rooms/views_reports.py',
        'rooms/views_admin.py'
    ]
    
    for file_path in files_to_fix:
        if not os.path.exists(file_path):
            print(f"Archivo no encontrado: {file_path}")
            continue
            
        print(f"Corrigiendo {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patrón para encontrar conversiones problemáticas a UTC
        utc_pattern = r'if from_date_obj\.tzinfo is None:\s*from_date_obj = from_date_obj\.replace\(tzinfo=timezone\.utc\)\s*if to_date_obj\.tzinfo is None:\s*to_date_obj = to_date_obj\.replace\(tzinfo=timezone\.utc\)'
        
        # Patrón para encontrar remoción de zona horaria
        naive_pattern = r'if start_datetime\.tzinfo is not None:\s*start_datetime = start_datetime\.replace\(tzinfo=None\)\s*if end_datetime\.tzinfo is not None:\s*end_datetime = end_datetime\.replace\(tzinfo=None\)'
        
        # Reemplazos
        replacements = [
            # Reemplazar imports problemáticos
            (r'from datetime import datetime, timezone', 'from datetime import datetime\nimport pytz'),
            
            # Reemplazar conversiones a UTC por conversiones a Bogotá
            (r'if from_date_obj\.tzinfo is None:\s*from_date_obj = from_date_obj\.replace\(tzinfo=timezone\.utc\)', 
             'if from_date_obj.tzinfo is None:\n                    from_date_obj = pytz.timezone(\'America/Bogota\').localize(from_date_obj)\n                else:\n                    from_date_obj = from_date_obj.astimezone(pytz.timezone(\'America/Bogota\'))'),
            
            (r'if to_date_obj\.tzinfo is None:\s*to_date_obj = to_date_obj\.replace\(tzinfo=timezone\.utc\)',
             'if to_date_obj.tzinfo is None:\n                    to_date_obj = pytz.timezone(\'America/Bogota\').localize(to_date_obj)\n                else:\n                    to_date_obj = to_date_obj.astimezone(pytz.timezone(\'America/Bogota\'))'),
            
            # Remover líneas que quitan la zona horaria
            (r'if start_datetime\.tzinfo is not None:\s*start_datetime = start_datetime\.replace\(tzinfo=None\)', ''),
            (r'if end_datetime\.tzinfo is not None:\s*end_datetime = end_datetime\.replace\(tzinfo=None\)', ''),
        ]
        
        # Aplicar reemplazos
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        
        # Escribir archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {file_path} corregido")

if __name__ == '__main__':
    fix_timezone_issues()
    print("🎉 Corrección de zona horaria completada")
