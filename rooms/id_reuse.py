# rooms/id_reuse.py
"""
Módulo para reutilización de IDs eliminados
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.apps import apps

def get_next_available_id(model_class, start_from=1):
    """
    Obtiene el próximo ID disponible más bajo para un modelo
    Busca desde el ID 1 hacia arriba hasta encontrar el primer disponible
    
    Args:
        model_class: Clase del modelo (ej: RoomEntry, Schedule, etc.)
        start_from: ID mínimo desde el cual buscar (por defecto 1)
    
    Returns:
        int: Próximo ID disponible
    """
    try:
        # Obtener todos los IDs existentes como conjunto para búsqueda rápida
        existing_ids = set(
            model_class.objects.values_list('id', flat=True)
        )
        
        # Buscar desde el ID 1 hacia arriba hasta encontrar uno disponible
        next_id = start_from
        while next_id in existing_ids:
            next_id += 1
            
        return next_id
        
    except Exception as e:
        # Si hay error, usar el comportamiento por defecto
        return None

def create_with_reused_id(model_class, **kwargs):
    """
    Crea un nuevo registro con el ID más bajo disponible
    
    Args:
        model_class: Clase del modelo
        **kwargs: Campos del modelo
    
    Returns:
        Instancia del modelo creada
    """
    try:
        with transaction.atomic():
            # Obtener el próximo ID disponible
            next_id = get_next_available_id(model_class)
            
            if next_id is None:
                # Si no se puede obtener ID reutilizable, crear normalmente
                return model_class.objects.create(**kwargs)
            
            # Crear el registro con ID específico
            instance = model_class(id=next_id, **kwargs)
            instance.save()
            return instance
            
    except Exception as e:
        # Si hay error, crear normalmente
        return model_class.objects.create(**kwargs)

def bulk_create_with_reused_ids(model_class, objects_data):
    """
    Crea múltiples registros reutilizando IDs
    
    Args:
        model_class: Clase del modelo
        objects_data: Lista de diccionarios con datos de los objetos
    
    Returns:
        Lista de instancias creadas
    """
    try:
        with transaction.atomic():
            # Obtener IDs disponibles
            existing_ids = set(
                model_class.objects.values_list('id', flat=True)
            )
            
            created_objects = []
            next_id = 1
            
            for obj_data in objects_data:
                # Buscar próximo ID disponible
                while next_id in existing_ids:
                    next_id += 1
                
                # Crear objeto con ID específico
                instance = model_class(id=next_id, **obj_data)
                instance.save()
                created_objects.append(instance)
                
                # Agregar ID usado a la lista
                existing_ids.add(next_id)
                next_id += 1
            
            return created_objects
            
    except Exception as e:
        # Si hay error, crear normalmente
        return model_class.objects.bulk_create([
            model_class(**obj_data) for obj_data in objects_data
        ])

"""
Sistema de Reutilización de IDs para optimización de base de datos
Permite reciclar IDs de registros eliminados para mantener eficiencia
"""

from django.db import transaction
from django.apps import apps


class IDReuseManager:
    """Administrador de reutilización de IDs para entradas de salas"""
    
    @classmethod
    def get_next_available_id(cls, model_class=None):
        """
        Obtiene el próximo ID disponible, reutilizando IDs eliminados si es posible
        
        Args:
            model_class: Clase del modelo para buscar IDs disponibles
            
        Returns:
            int: Próximo ID disponible para usar
        """
        if model_class is None:
            model_class = apps.get_model('rooms', 'RoomEntry')

        with transaction.atomic():
            # Obtener todos los IDs existentes ordenados
            existing_ids = set(
                model_class.objects.values_list('id', flat=True).order_by('id')
            )
            
            if not existing_ids:
                return 1
            
            # Buscar el primer hueco en la secuencia
            expected_id = 1
            for existing_id in sorted(existing_ids):
                if expected_id < existing_id:
                    # Encontramos un hueco, usar este ID
                    return expected_id
                expected_id = existing_id + 1
            
            # No hay huecos, usar el siguiente ID secuencial
            return expected_id
    
    @classmethod
    def find_reusable_ids(cls, model_class=None, limit=100):
        """
        Encuentra IDs que pueden ser reutilizados (huecos en la secuencia)
        
        Args:
            model_class: Clase del modelo a analizar
            limit: Límite de IDs a revisar
            
        Returns:
            list: Lista de IDs disponibles para reutilizar
        """
        if model_class is None:
            model_class = apps.get_model('rooms', 'RoomEntry')

        existing_ids = set(
            model_class.objects.values_list('id', flat=True).order_by('id')[:limit]
        )
        
        if not existing_ids:
            return [1]
        
        max_id = max(existing_ids)
        all_possible_ids = set(range(1, max_id + 1))
        
        # Encontrar IDs faltantes (disponibles para reutilizar)
        reusable_ids = sorted(all_possible_ids - existing_ids)
        
        return reusable_ids
    
    @classmethod
    def get_id_statistics(cls, model_class=None):
        """
        Obtiene estadísticas sobre el uso de IDs
        
        Args:
            model_class: Clase del modelo a analizar
            
        Returns:
            dict: Estadísticas del uso de IDs
        """
        if model_class is None:
            model_class = apps.get_model('rooms', 'RoomEntry')

        existing_ids = list(
            model_class.objects.values_list('id', flat=True).order_by('id')
        )
        
        if not existing_ids:
            return {
                'total_records': 0,
                'max_id': 0,
                'reusable_ids': [1],
                'efficiency': 100.0,
                'gaps_count': 0
            }
        
        max_id = max(existing_ids)
        expected_total = max_id
        actual_total = len(existing_ids)
        gaps_count = expected_total - actual_total
        efficiency = (actual_total / expected_total) * 100 if expected_total > 0 else 100.0
        
        reusable_ids = cls.find_reusable_ids(model_class, limit=50)
        
        return {
            'total_records': actual_total,
            'max_id': max_id,
            'reusable_ids': reusable_ids[:10],  # Mostrar solo los primeros 10
            'efficiency': round(efficiency, 2),
            'gaps_count': gaps_count
        }
    
    @classmethod
    def optimize_model_ids(cls, model_class=None, dry_run=True):
        """
        Optimiza los IDs de un modelo compactando la secuencia
        
        Args:
            model_class: Clase del modelo a optimizar
            dry_run: Si True, solo simula la optimización sin aplicar cambios
            
        Returns:
            dict: Resultado de la optimización
        """
        if model_class is None:
            model_class = apps.get_model('rooms', 'RoomEntry')

        if dry_run:
            stats = cls.get_id_statistics(model_class)
            return {
                'action': 'simulation',
                'current_stats': stats,
                'optimization_needed': stats['gaps_count'] > 0,
                'potential_savings': stats['gaps_count']
            }
        
        # Implementación real de optimización (requiere cuidado con foreign keys)
        # Por seguridad, solo retornamos simulación por ahora
        return {
            'action': 'not_implemented',
            'message': 'Optimización real requiere manejo cuidadoso de foreign keys'
        }


class RoomEntryIDManager(IDReuseManager):
    """Administrador específico para IDs de RoomEntry"""
    
    @classmethod
    def create_with_reused_id(cls, **kwargs):
        """
        Crea una nueva entrada de sala reutilizando ID disponible
        
        Args:
            **kwargs: Parámetros para crear el RoomEntry
            
        Returns:
            RoomEntry: Nueva instancia creada
        """
        # Resolver modelo dinámicamente para evitar import circular
        model_class = apps.get_model('rooms', 'RoomEntry')

        # Obtener ID disponible
        new_id = cls.get_next_available_id(model_class)

        # Crear la instancia con ID específico
        kwargs['id'] = new_id
        return model_class.objects.create(**kwargs)
    
    @classmethod
    def get_room_entry_stats(cls):
        """Estadísticas específicas para RoomEntry"""
        model_class = apps.get_model('rooms', 'RoomEntry')
        return cls.get_id_statistics(model_class)