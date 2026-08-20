#!/bin/bash
set -e

# Install Python dependencies
pip install -q -r requirements.txt

# Run Django migrations
python inventiq_project/manage.py migrate --noinput

# Collect static files
python inventiq_project/manage.py collectstatic --noinput

# Start gunicorn
gunicorn inventiq_project.wsgi --log-file - --bind 0.0.0.0:${PORT:-8000}

