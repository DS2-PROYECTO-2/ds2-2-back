import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rooms.models import Room, RoomEntry
from rooms.services import RoomEntryBusinessLogic
from notifications.models import Notification

User = get_user_model()

def create_excessive_hours_case():
    """
    Crear un caso de prueba donde un monitor excede las 8 horas
    """
    try:
        print("=== CREANDO CASO DE EXCESO DE HORAS ===")
        
        # 1. Buscar o crear un usuario monitor
        monitor = User.objects.filter(role='monitor', is_verified=True).first()
        if not monitor:
            monitor = User.objects.create_user(
                username='test_monitor_excess',
                email='test_excess@example.com',
                password='testpass123',
                identification='99999999',
                first_name='Monitor',
                last_name='ExcesoHoras',
                role='monitor',
                is_verified=True
            )
            print(f"✅ Monitor creado: {monitor.get_full_name()} ({monitor.username})")
        else:
            print(f"✅ Usando monitor existente: {monitor.get_full_name()} ({monitor.username})")
        
        # 2. Buscar o crear un usuario admin
        admin = User.objects.filter(role='admin', is_verified=True).first()
        if not admin:
            admin = User.objects.create_user(
                username='test_admin_notif',
                email='admin_notif@example.com',
                password='testpass123',
                identification='88888888',
                first_name='Admin',
                last_name='Notificaciones',
                role='admin',
                is_verified=True
            )
            print(f"✅ Admin creado: {admin.get_full_name()} ({admin.username})")
        else:
            print(f"✅ Usando admin existente: {admin.get_full_name()} ({admin.username})")
        
        # 3. Buscar o crear una sala
        room = Room.objects.filter(is_active=True).first()
        if not room:
            room = Room.objects.create(
                name='Sala Test Exceso',
                code='STE001',
                capacity=25,
                is_active=True,
                description='Sala para pruebas de exceso de horas'
            )
            print(f"✅ Sala creada: {room.name} ({room.code})")
        else:
            print(f"✅ Usando sala existente: {room.name} ({room.code})")
        
        # 4. Limpiar entradas activas previas del monitor
        active_entries = RoomEntry.objects.filter(user=monitor, exit_time__isnull=True)
        if active_entries.exists():
            print(f"⚠️ Finalizando {active_entries.count()} entrada(s) activa(s) previa(s)")
            for entry in active_entries:
                entry.exit_time = timezone.now()
                entry.save()
        
        # 5. Crear una entrada que simule 10 horas de duración (excede las 8 horas)
        entry_time = timezone.now() - timedelta(hours=10, minutes=30)  # Entrada hace 10.5 horas
        exit_time = timezone.now()  # Salida ahora
        
        print(f"📅 Simulando sesión:")
        print(f"   Entrada: {entry_time}")
        print(f"   Salida: {exit_time}")
        print(f"   Duración: 10.5 horas (excede 2.5 horas)")
        
        # Crear la entrada sin tiempo personalizado primero
        entry = RoomEntry.objects.create(
            user=monitor,
            room=room,
            notes='Sesión de prueba de exceso de horas'
        )
        
        # Luego actualizar los tiempos manualmente para evitar auto_now_add
        entry.entry_time = entry_time
        entry.exit_time = exit_time
        entry.save()
        
        print(f"✅ Entrada creada con ID: {entry.id}")
        
        # Debug: Verificar los tiempos reales en la base de datos
        entry.refresh_from_db()
        print(f"Debug - Entrada real: {entry.entry_time}")
        print(f"Debug - Salida real: {entry.exit_time}")
        print(f"Debug - Diferencia: {entry.exit_time - entry.entry_time}")
        
        # 6. Ejecutar la lógica de validación para generar notificación
        print("\n=== EJECUTANDO VALIDACIÓN DE EXCESO DE HORAS ===")
        
        # Primero probemos el cálculo de duración directamente
        duration_info = RoomEntryBusinessLogic.calculate_session_duration(entry)
        print(f"Debug - Duration info: {duration_info}")
        
        notification_result = RoomEntryBusinessLogic.check_and_notify_excessive_hours(entry)
        
        print(f"Resultado de notificación:")
        print(f"- Notificación enviada: {notification_result['notification_sent']}")
        print(f"- Duración total: {notification_result.get('duration_hours', 'N/A')} horas")
        print(f"- Exceso: {notification_result.get('excess_hours', 'N/A')} horas")
        print(f"- Admins notificados: {notification_result.get('admins_notified', 'N/A')}")
        
        # 7. Verificar que se crearon las notificaciones
        print("\n=== VERIFICANDO NOTIFICACIONES CREADAS ===")
        
        excessive_notifications = Notification.objects.filter(
            notification_type='excessive_hours'
        ).order_by('-created_at')[:3]
        
        print(f"Total de notificaciones de exceso de horas: {excessive_notifications.count()}")
        
        for notif in excessive_notifications:
            print(f"\n📧 Notificación ID {notif.id}:")
            print(f"   Para: {notif.user.get_full_name()} ({notif.user.username})")
            print(f"   Título: {notif.title}")
            print(f"   Fecha: {notif.created_at}")
            print(f"   Relacionado con entrada ID: {notif.related_object_id}")
            if notif.related_object_id:
                try:
                    related_entry = RoomEntry.objects.get(id=notif.related_object_id)
                    print(f"   Monitor: {related_entry.user.get_full_name()}")
                    print(f"   Sala: {related_entry.room.name}")
                    duration_info = RoomEntryBusinessLogic.calculate_session_duration(related_entry)
                    print(f"   Horas: {duration_info.get('total_duration_hours', 'N/A')}")
                except RoomEntry.DoesNotExist:
                    print(f"   Monitor: N/A")
                    print(f"   Sala: N/A")
                    print(f"   Horas: N/A")
        
        print(f"\n✅ CASO DE EXCESO DE HORAS CREADO EXITOSAMENTE")
        print(f"   Monitor: {monitor.username}")
        print(f"   Entrada ID: {entry.id}")
        print(f"   Duración: 10.5 horas")
        print(f"   Notificaciones generadas: {notification_result.get('admins_notified', 0)}")
        
        return {
            'success': True,
            'monitor': monitor,
            'entry': entry,
            'notification_result': notification_result
        }
        
    except Exception as e:
        print(f"❌ Error creando caso de exceso: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    result = create_excessive_hours_case()
    
    if result['success']:
        print(f"\n🎯 SIGUIENTE PASO:")
        print(f"   Usa la API para ver las notificaciones:")
        print(f"   GET /api/notifications/notifications/excessive_hours/")
        print(f"   Con token de administrador")
    else:
        print(f"\n❌ Error en la creación del caso de prueba")