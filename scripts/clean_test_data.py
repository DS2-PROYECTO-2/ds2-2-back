"""
Script para limpiar todos los datos de prueba
Ejecutar con: python manage.py shell < scripts/clean_test_data.py
"""

from django.contrib.auth import get_user_model
from rooms.models import Room
from schedule.models import Schedule
from courses.models import Course, CourseHistory
from rest_framework.authtoken.models import Token

print("🧹 Iniciando limpieza de datos de prueba...")

User = get_user_model()

# Contar elementos antes de limpiar
users_count = User.objects.filter(username__contains='test').count()
rooms_count = Room.objects.filter(code__startswith='SC-').count() + Room.objects.filter(code__startswith='LAB-').count()
schedules_count = Schedule.objects.filter(user__username__contains='test').count()
courses_count = Course.objects.filter(created_by__username__contains='test').count()
history_count = CourseHistory.objects.all().count()

print(f"\n📊 Elementos encontrados:")
print(f"👥 Usuarios de prueba: {users_count}")
print(f"🏢 Salas de prueba: {rooms_count}")
print(f"📅 Horarios de prueba: {schedules_count}")
print(f"🎓 Cursos de prueba: {courses_count}")
print(f"📝 Registros de historial: {history_count}")

# Limpiar datos en orden correcto (respetando dependencias)
print("\n🗑️ Eliminando datos...")

# 1. Eliminar historial de cursos
deleted_history = CourseHistory.objects.all().delete()
print(f"✅ Historial eliminado: {deleted_history[0]} registros")

# 2. Eliminar cursos
deleted_courses = Course.objects.filter(created_by__username__contains='test').delete()
print(f"✅ Cursos eliminados: {deleted_courses[0]} registros")

# 3. Eliminar horarios
deleted_schedules = Schedule.objects.filter(user__username__contains='test').delete()
print(f"✅ Horarios eliminados: {deleted_schedules[0]} registros")

# 4. Eliminar salas de prueba
deleted_rooms_sc = Room.objects.filter(code__startswith='SC-').delete()
deleted_rooms_lab = Room.objects.filter(code__startswith='LAB-').delete()
total_rooms = deleted_rooms_sc[0] + deleted_rooms_lab[0]
print(f"✅ Salas eliminadas: {total_rooms} registros")

# 5. Eliminar tokens de usuarios de prueba
test_users = User.objects.filter(username__contains='test')
tokens_deleted = 0
for user in test_users:
    try:
        token = Token.objects.get(user=user)
        token.delete()
        tokens_deleted += 1
    except Token.DoesNotExist:
        pass
print(f"✅ Tokens eliminados: {tokens_deleted} registros")

# 6. Eliminar usuarios de prueba
deleted_users = User.objects.filter(username__contains='test').delete()
print(f"✅ Usuarios eliminados: {deleted_users[0]} registros")

print("\n📊 Verificación final:")
remaining_users = User.objects.filter(username__contains='test').count()
remaining_rooms = Room.objects.filter(code__startswith='SC-').count() + Room.objects.filter(code__startswith='LAB-').count()
remaining_schedules = Schedule.objects.filter(user__username__contains='test').count()
remaining_courses = Course.objects.filter(created_by__username__contains='test').count()
remaining_history = CourseHistory.objects.all().count()

print(f"👥 Usuarios restantes: {remaining_users}")
print(f"🏢 Salas restantes: {remaining_rooms}")
print(f"📅 Horarios restantes: {remaining_schedules}")
print(f"🎓 Cursos restantes: {remaining_courses}")
print(f"📝 Historia restante: {remaining_history}")

if (remaining_users == 0 and remaining_rooms == 0 and 
    remaining_schedules == 0 and remaining_courses == 0):
    print("\n✅ ¡Limpieza completada exitosamente!")
    print("🎉 Todos los datos de prueba han sido eliminados.")
else:
    print("\n⚠️ Algunos datos no pudieron ser eliminados.")
    print("💡 Tip: Verifica dependencias o ejecuta el script nuevamente.")

print("\n" + "="*50)
print("📝 RESUMEN DE LIMPIEZA:")
print("="*50)
print(f"Cursos eliminados: {deleted_courses[0] if deleted_courses else 0}")
print(f"Horarios eliminados: {deleted_schedules[0] if deleted_schedules else 0}")
print(f"Salas eliminadas: {total_rooms}")
print(f"Usuarios eliminados: {deleted_users[0] if deleted_users else 0}")
print(f"Tokens eliminados: {tokens_deleted}")
print(f"Historial eliminado: {deleted_history[0] if deleted_history else 0}")
print("="*50)
print("\n💡 Para crear nuevos datos de prueba, ejecuta:")
print("   python manage.py shell < scripts/create_test_data.py")