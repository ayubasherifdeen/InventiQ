import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventiq_project.settings')
django.setup()

from django.contrib.auth.models import User

User.objects.filter(username='admin').delete()
User.objects.create_superuser('admin', 'admin@example.com', 'adminmanager')
print("Superuser 'admin' created successfully")

