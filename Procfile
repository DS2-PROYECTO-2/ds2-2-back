# Procfile for Render deployment
# This file tells Render how to start the Django application

# Web process - starts the Django application
web: gunicorn ds2_back.wsgi:application --bind 0.0.0.0:$PORT

# Worker process (optional) - for background tasks
# worker: python manage.py process_tasks

# Release process (optional) - runs before deployment
# release: python manage.py migrate && python manage.py collectstatic --noinput
