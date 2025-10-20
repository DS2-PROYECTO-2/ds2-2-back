from django.urls import path
from . import views

app_name = 'export'

urlpatterns = [
    # Trabajos de exportación
    path('jobs/', views.ExportJobListCreateView.as_view(), name='export-job-list-create'),
    path('jobs/<int:pk>/', views.ExportJobDetailView.as_view(), name='export-job-detail'),
    path('jobs/<int:export_job_id>/status/', views.get_export_status, name='export-status'),
    path('jobs/<int:export_job_id>/download/', views.download_export_file, name='download-export'),
    
    # Exportación de datos
    path('monitors/export/', views.export_monitors_data, name='export-monitors'),
    path('monitors/data/', views.get_monitors_data, name='get-monitors-data'),
    path('room-entries/data/', views.get_room_entries_data, name='get-room-entries-data'),
    path('schedules/data/', views.get_schedules_data, name='get-schedules-data'),
]

