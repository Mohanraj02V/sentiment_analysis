#!/bin/bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files (optional, if needed)
python manage.py collectstatic --no-input

# Recreate fresh migrations and apply them in order
python manage.py makemigrations
python manage.py migrate
