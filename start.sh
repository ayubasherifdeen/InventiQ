#!/bin/bash
set -e

cd inventiq_project

# Install Python dependencies
pip install -q -r ../requirements.txt

# Run Django migrations
python manage.py migrate --noinput
python manage.py seed_data

# Collect static files
python manage.py collectstatic --noinput

# Start gunicorn
gunicorn inventiq_project.wsgi --log-file - --bind 0.0.0.0:${PORT:-8000}

