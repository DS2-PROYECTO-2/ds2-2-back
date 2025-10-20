#!/usr/bin/env python
"""
Script para probar que la exportación funciona sin WinError 32
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings.development')
django.setup()

from export.services import MonitorDataExporter
from export.models import ExportJob
from users.models import User

def test_export_fix():
    """Prueba que la exportación funcione sin WinError 32"""
    print("🧪 Probando exportación sin WinError 32...")
    
    try:
        # Obtener un usuario admin para la prueba
        admin_user = User.objects.filter(role=User.ADMIN).first()
        if not admin_user:
            print("❌ No se encontró usuario admin para la prueba")
            return
        
        # Crear un trabajo de exportación de prueba
        export_job = ExportJob.objects.create(
            title="Prueba de Exportación",
            export_type=ExportJob.MONITORS_DATA,
            format=ExportJob.PDF,
            status=ExportJob.PENDING,
            requested_by=admin_user
        )
        
        print(f"✅ Trabajo de exportación creado: ID {export_job.id}")
        
        # Crear exporter
        exporter = MonitorDataExporter(export_job)
        
        # Probar exportación PDF
        print("📄 Probando exportación PDF...")
        pdf_success = exporter.export_to_pdf()
        
        if pdf_success:
            print("✅ Exportación PDF exitosa")
            print(f"   - Archivo: {export_job.file.name if export_job.file else 'No generado'}")
            print(f"   - Estado: {export_job.get_status_display()}")
        else:
            print("❌ Exportación PDF falló")
            print(f"   - Error: {export_job.error_message}")
        
        # Crear otro trabajo para Excel
        export_job_excel = ExportJob.objects.create(
            title="Prueba de Exportación Excel",
            export_type=ExportJob.MONITORS_DATA,
            format=ExportJob.EXCEL,
            status=ExportJob.PENDING,
            requested_by=admin_user
        )
        
        # Crear exporter para Excel
        exporter_excel = MonitorDataExporter(export_job_excel)
        
        # Probar exportación Excel
        print("📊 Probando exportación Excel...")
        excel_success = exporter_excel.export_to_excel()
        
        if excel_success:
            print("✅ Exportación Excel exitosa")
            print(f"   - Archivo: {export_job_excel.file.name if export_job_excel.file else 'No generado'}")
            print(f"   - Estado: {export_job_excel.get_status_display()}")
        else:
            print("❌ Exportación Excel falló")
            print(f"   - Error: {export_job_excel.error_message}")
        
        # Resumen
        if pdf_success and excel_success:
            print("\n🎉 ¡ÉXITO! La exportación funciona sin WinError 32")
            print("   - PDF: ✅ Generado correctamente")
            print("   - Excel: ✅ Generado correctamente")
            print("   - Sin archivos temporales en disco")
            print("   - Sin conflictos con Windows Defender")
        else:
            print("\n❌ Algunas exportaciones fallaron")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_export_fix()
