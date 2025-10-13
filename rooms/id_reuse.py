"""
Sistema de Reutilización de IDs para optimización de base de datos
Permite reciclar IDs de registros eliminados para mantener eficiencia
"""

from django.db import transaction
from .models import RoomEntry


class IDReuseManager:
    """Administrador de reutilización de IDs para entradas de salas"""
    
    @classmethod
    def get_next_available_id(cls, model_class=RoomEntry):
        """
        Obtiene el próximo ID disponible, reutilizando IDs eliminados si es posible
        
        Args:
            model_class: Clase del modelo para buscar IDs disponibles
            
        Returns:
            int: Próximo ID disponible para usar
        """
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
    def find_reusable_ids(cls, model_class=RoomEntry, limit=100):
        """
        Encuentra IDs que pueden ser reutilizados (huecos en la secuencia)
        
        Args:
            model_class: Clase del modelo a analizar
            limit: Límite de IDs a revisar
            
        Returns:
            list: Lista de IDs disponibles para reutilizar
        """
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
    def get_id_statistics(cls, model_class=RoomEntry):
        """
        Obtiene estadísticas sobre el uso de IDs
        
        Args:
            model_class: Clase del modelo a analizar
            
        Returns:
            dict: Estadísticas del uso de IDs
        """
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
    def optimize_model_ids(cls, model_class=RoomEntry, dry_run=True):
        """
        Optimiza los IDs de un modelo compactando la secuencia
        
        Args:
            model_class: Clase del modelo a optimizar
            dry_run: Si True, solo simula la optimización sin aplicar cambios
            
        Returns:
            dict: Resultado de la optimización
        """
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
        # Obtener ID disponible
        new_id = cls.get_next_available_id(RoomEntry)
        
        # Crear la instancia con ID específico
        kwargs['id'] = new_id
        return RoomEntry.objects.create(**kwargs)
    
    @classmethod
    def get_room_entry_stats(cls):
        """Estadísticas específicas para RoomEntry"""
        return cls.get_id_statistics(RoomEntry)