#!/bin/bash

# Django migration
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@creditapi.com', 'admin123')
    print("Superuser 'admin' created successfully")
END

echo "Database initialization completed!"
