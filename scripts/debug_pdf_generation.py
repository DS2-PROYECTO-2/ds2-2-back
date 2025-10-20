#!/usr/bin/env python
"""
Script para diagnosticar problemas con la generación de PDF
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
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def test_simple_pdf():
    """Prueba generar un PDF simple para verificar que reportlab funciona"""
    print("🧪 Probando generación de PDF simple...")
    
    try:
        # Crear PDF simple en memoria
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Estilos básicos
        styles = getSampleStyleSheet()
        
        # Contenido simple
        title = Paragraph("Test PDF Generation", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        content = Paragraph("Este es un PDF de prueba generado con BytesIO.", styles['Normal'])
        story.append(content)
        
        # Construir PDF
        doc.build(story)
        
        # Verificar contenido
        buffer.seek(0)
        pdf_content = buffer.getvalue()
        
        print(f"✅ PDF simple generado exitosamente")
        print(f"   - Tamaño: {len(pdf_content)} bytes")
        print(f"   - Primeros 50 bytes: {pdf_content[:50]}")
        
        # Verificar que es un PDF válido
        if pdf_content.startswith(b'%PDF'):
            print("✅ Formato PDF válido detectado")
        else:
            print("❌ Formato PDF inválido")
            print(f"   - Contenido inicial: {pdf_content[:20]}")
        
        buffer.close()
        return True
        
    except Exception as e:
        print(f"❌ Error generando PDF simple: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_export_pdf():
    """Prueba la exportación real de monitores"""
    print("\n🧪 Probando exportación real de monitores...")
    
    try:
        # Obtener usuario admin
        admin_user = User.objects.filter(role=User.ADMIN).first()
        if not admin_user:
            print("❌ No se encontró usuario admin")
            return False
        
        # Crear trabajo de exportación
        export_job = ExportJob.objects.create(
            title="Debug PDF Export",
            export_type=ExportJob.MONITORS_DATA,
            format=ExportJob.PDF,
            status=ExportJob.PENDING,
            requested_by=admin_user
        )
        
        print(f"✅ Trabajo creado: ID {export_job.id}")
        
        # Crear exporter
        exporter = MonitorDataExporter(export_job)
        
        # Verificar datos antes de exportar
        monitors = exporter.get_monitors_queryset()
        print(f"   - Monitores encontrados: {monitors.count()}")
        
        if monitors.count() == 0:
            print("⚠️  No hay monitores para exportar")
            return False
        
        # Exportar
        success = exporter.export_to_pdf()
        
        if success:
            print("✅ Exportación exitosa")
            print(f"   - Estado: {export_job.get_status_display()}")
            print(f"   - Archivo: {export_job.file.name if export_job.file else 'No generado'}")
            print(f"   - Tamaño: {export_job.file_size} bytes")
            
            # Verificar contenido del archivo
            if export_job.file:
                try:
                    with export_job.file.open('rb') as f:
                        file_content = f.read()
                        print(f"   - Contenido del archivo: {len(file_content)} bytes")
                        print(f"   - Inicio del archivo: {file_content[:50]}")
                        
                        if file_content.startswith(b'%PDF'):
                            print("✅ Archivo PDF válido")
                        else:
                            print("❌ Archivo PDF inválido")
                            
                except Exception as e:
                    print(f"❌ Error leyendo archivo: {e}")
        else:
            print("❌ Exportación falló")
            print(f"   - Error: {export_job.error_message}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error en exportación: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal de diagnóstico"""
    print("🔍 Diagnóstico de generación de PDF")
    print("=" * 50)
    
    # Prueba 1: PDF simple
    simple_success = test_simple_pdf()
    
    # Prueba 2: Exportación real
    export_success = test_export_pdf()
    
    # Resumen
    print("\n📊 Resumen del diagnóstico:")
    print(f"   - PDF simple: {'✅' if simple_success else '❌'}")
    print(f"   - Exportación real: {'✅' if export_success else '❌'}")
    
    if simple_success and export_success:
        print("\n🎉 ¡Todo funciona correctamente!")
    elif simple_success and not export_success:
        print("\n⚠️  Reportlab funciona, pero hay problema en la exportación real")
    else:
        print("\n❌ Hay problemas con la generación de PDF")

if __name__ == "__main__":
    main()
