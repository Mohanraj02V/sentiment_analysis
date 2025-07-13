#!/bin/bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Generate migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate
