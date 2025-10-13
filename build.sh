#!/usr/bin/env bash
# Build script for Render deployment
# This script runs during the build process on Render

echo "🚀 Starting build process for DS2 Backend..."

# Exit on any error
set -e

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create logs directory if it doesn't exist
echo "📁 Creating logs directory..."
mkdir -p logs

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist (optional)
echo "👤 Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Creating superuser...')
    User.objects.create_superuser(
        username='admin',
        email='admin@ds2-backend.onrender.com',
        password='admin123456',
        identification='0000000000',
        first_name='Admin',
        last_name='User',
        phone='0000000000',
        role='admin'
    )
    print('Superuser created: admin/admin123456')
else:
    print('Superuser already exists')
"

# Run any custom setup commands
echo "⚙️ Running custom setup commands..."

# Check if all apps are properly configured
echo "🔍 Checking app configuration..."
python manage.py check --deploy

# Display build information
echo "✅ Build completed successfully!"
echo "📊 Build information:"
echo "   - Python version: $(python --version)"
echo "   - Django version: $(python -c 'import django; print(django.get_version())')"
echo "   - Static files collected: $(ls -la staticfiles/ | wc -l) files"
echo "   - Database migrations: Applied"

echo "🎉 Ready for deployment!"
