#!/usr/bin/env python
"""
Test simple del endpoint de resumen
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ds2_back.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

try:
    admin_user = User.objects.filter(role='admin', is_verified=True).first()
    token, created = Token.objects.get_or_create(user=admin_user)
    client = Client()
    headers = {'HTTP_AUTHORIZATION': f'Token {token.key}'}

    print('Testing summary endpoint...')
    response = client.get('/api/notifications/notifications/excessive_hours_summary/', **headers)
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print('✅ Summary endpoint working!')
        print(f'Total notifications: {data.get("total_notifications", 0)}')
        print(f'Unique monitors: {data.get("unique_monitors", 0)}')
        print(f'Period: {data.get("period", "N/A")}')
    else:
        print(f'❌ Error: {response.content.decode()}')
        
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()