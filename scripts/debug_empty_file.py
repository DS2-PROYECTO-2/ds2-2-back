#!/usr/bin/env python
"""
Script para diagnosticar por qué los archivos se generan vacíos
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

def test_simple_pdf_generation():
    """Probar generación de PDF simple paso a paso"""
    print("🧪 Probando generación de PDF simple...")
    
    try:
        # Crear buffer
        buffer = BytesIO()
        print(f"✅ Buffer creado: {type(buffer)}")
        
        # Crear documento
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        print("✅ Documento creado")
        
        # Crear contenido
        story = []
        styles = getSampleStyleSheet()
        
        title = Paragraph("Test PDF", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        content = Paragraph("Este es un PDF de prueba.", styles['Normal'])
        story.append(content)
        
        print(f"✅ Story creada con {len(story)} elementos")
        
        # Construir PDF
        print("🔨 Construyendo PDF...")
        doc.build(story)
        print("✅ PDF construido")
        
        # Verificar contenido
        buffer.seek(0)
        pdf_content = buffer.getvalue()
        print(f"✅ Contenido obtenido: {len(pdf_content)} bytes")
        
        if len(pdf_content) == 0:
            print("❌ PROBLEMA: El PDF está vacío!")
            return False
        
        if pdf_content.startswith(b'%PDF'):
            print("✅ PDF válido generado")
        else:
            print("❌ PDF inválido")
            print(f"   - Inicio: {pdf_content[:50]}")
            return False
        
        buffer.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_export_with_debug():
    """Probar exportación con debugging detallado"""
    print("\n🧪 Probando exportación con debugging...")
    
    try:
        # Obtener usuario admin
        admin_user = User.objects.filter(role=User.ADMIN).first()
        if not admin_user:
            print("❌ No se encontró usuario admin")
            return False
        
        # Crear trabajo de exportación
        export_job = ExportJob.objects.create(
            title="Debug Empty File",
            export_type=ExportJob.MONITORS_DATA,
            format=ExportJob.PDF,
            status=ExportJob.PENDING,
            requested_by=admin_user
        )
        
        print(f"✅ Trabajo creado: ID {export_job.id}")
        
        # Crear exporter
        exporter = MonitorDataExporter(export_job)
        
        # Verificar datos
        monitors = exporter.get_monitors_queryset()
        print(f"✅ Monitores encontrados: {monitors.count()}")
        
        if monitors.count() == 0:
            print("⚠️  No hay monitores - esto puede causar archivo vacío")
        
        # Probar generación paso a paso
        print("🔨 Iniciando generación...")
        
        # Crear buffer manualmente para debug
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Agregar contenido mínimo
        styles = getSampleStyleSheet()
        title = Paragraph("Reporte de Monitores", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        if monitors.count() > 0:
            content = Paragraph(f"Total de monitores: {monitors.count()}", styles['Normal'])
            story.append(content)
        else:
            content = Paragraph("No hay monitores para mostrar", styles['Normal'])
            story.append(content)
        
        print(f"✅ Story preparada con {len(story)} elementos")
        
        # Construir PDF
        doc.build(story)
        print("✅ PDF construido")
        
        # Verificar contenido
        buffer.seek(0)
        pdf_content = buffer.getvalue()
        print(f"✅ Contenido: {len(pdf_content)} bytes")
        
        if len(pdf_content) == 0:
            print("❌ PROBLEMA: PDF generado está vacío!")
            return False
        
        # Simular el proceso de guardado
        from django.core.files import File
        django_file = File(BytesIO(pdf_content))
        
        # Guardar archivo
        export_job.file.save(
            f"debug_export_{export_job.id}.pdf",
            django_file,
            save=True
        )
        
        print(f"✅ Archivo guardado: {export_job.file.name}")
        
        # Verificar archivo guardado
        with export_job.file.open('rb') as f:
            saved_content = f.read()
            print(f"✅ Archivo guardado: {len(saved_content)} bytes")
            
            if len(saved_content) == 0:
                print("❌ PROBLEMA: Archivo guardado está vacío!")
                return False
        
        # Marcar como completado
        export_job.mark_as_completed(file_size=len(pdf_content))
        print("✅ Trabajo marcado como completado")
        
        buffer.close()
        return True
        
    except Exception as e:
        print(f"❌ Error en exportación: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_real_export():
    """Probar la exportación real"""
    print("\n🧪 Probando exportación real...")
    
    try:
        # Obtener usuario admin
        admin_user = User.objects.filter(role=User.ADMIN).first()
        if not admin_user:
            print("❌ No se encontró usuario admin")
            return False
        
        # Crear trabajo de exportación
        export_job = ExportJob.objects.create(
            title="Real Export Test",
            export_type=ExportJob.MONITORS_DATA,
            format=ExportJob.PDF,
            status=ExportJob.PENDING,
            requested_by=admin_user
        )
        
        print(f"✅ Trabajo creado: ID {export_job.id}")
        
        # Crear exporter
        exporter = MonitorDataExporter(export_job)
        
        # Ejecutar exportación real
        print("🔨 Ejecutando exportación real...")
        success = exporter.export_to_pdf()
        
        if success:
            print("✅ Exportación exitosa")
            print(f"   - Estado: {export_job.get_status_display()}")
            print(f"   - Archivo: {export_job.file.name if export_job.file else 'No generado'}")
            print(f"   - Tamaño: {export_job.file_size} bytes")
            
            # Verificar archivo
            if export_job.file:
                with export_job.file.open('rb') as f:
                    file_content = f.read()
                    print(f"   - Contenido real: {len(file_content)} bytes")
                    
                    if len(file_content) == 0:
                        print("❌ PROBLEMA: Archivo real está vacío!")
                        return False
                    else:
                        print("✅ Archivo real tiene contenido")
                        return True
            else:
                print("❌ PROBLEMA: No se generó archivo")
                return False
        else:
            print("❌ Exportación falló")
            print(f"   - Error: {export_job.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Error en exportación real: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🔍 Diagnóstico de archivos vacíos")
    print("=" * 50)
    
    # Prueba 1: PDF simple
    simple_success = test_simple_pdf_generation()
    
    # Prueba 2: Exportación con debug
    debug_success = test_export_with_debug()
    
    # Prueba 3: Exportación real
    real_success = test_real_export()
    
    # Resumen
    print("\n📊 Resumen del diagnóstico:")
    print(f"   - PDF simple: {'✅' if simple_success else '❌'}")
    print(f"   - Exportación debug: {'✅' if debug_success else '❌'}")
    print(f"   - Exportación real: {'✅' if real_success else '❌'}")
    
    if not simple_success:
        print("\n❌ PROBLEMA: Reportlab no funciona correctamente")
    elif not debug_success:
        print("\n❌ PROBLEMA: Hay un error en la lógica de exportación")
    elif not real_success:
        print("\n❌ PROBLEMA: El método export_to_pdf tiene un error")
    else:
        print("\n🎉 ¡Todo funciona correctamente!")

if __name__ == "__main__":
    main()
