#!/usr/bin/env python3
"""
Script para mostrar todas las URLs disponibles en el proyecto
"""

import os
import django
from django.urls import get_resolver

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

def show_urls(urllist, depth=0):
    """Mostrar todas las URLs recursivamente"""
    for entry in urllist:
        print("  " * depth, entry.regex.pattern)
        if hasattr(entry, 'url_patterns'):
            show_urls(entry.url_patterns, depth + 1)

def main():
    print("URLs disponibles en el proyecto:")
    print("=" * 50)
    
    resolver = get_resolver()
    show_urls(resolver.url_patterns)
    
    print("\n" + "=" * 50)
    print("Endpoints de notificaciones específicos:")
    print("-" * 30)
    
    # URLs específicas de notificaciones
    notification_urls = [
        "GET  /api/notifications/",
        "GET  /api/notifications/{id}/",
        "POST /api/notifications/",
        "PUT  /api/notifications/{id}/",
        "PATCH /api/notifications/{id}/",
        "DELETE /api/notifications/{id}/",
        "GET  /api/notifications/unread/",
        "GET  /api/notifications/unread-count/",
        "PATCH /api/notifications/{id}/mark-read/",
        "PATCH /api/notifications/mark-all-read/",
        "GET  /api/notifications/summary/",
        "GET  /api/notifications/excessive-hours/",
        "GET  /api/notifications/excessive-hours-summary/",
        "POST /api/notifications/hours-exceeded/",
    ]
    
    for url in notification_urls:
        print(url)

if __name__ == "__main__":
    main()
