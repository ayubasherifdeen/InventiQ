#!/bin/bash
set -e

# Install Python dependencies
pip install -q -r requirements.txt

# Run Django migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start gunicorn
gunicorn inventiq_project.wsgi --log-file - --bind 0.0.0.0:${PORT:-8000}

