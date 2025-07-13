#!/bin/bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files (optional, if needed)
python manage.py collectstatic --no-input

# Reset broken migration state (fix InconsistentMigrationHistory)
# These are safe if run with --fake and zero
python manage.py migrate --fake admin zero || true
python manage.py migrate --fake analysis zero || true

# Recreate fresh migrations and apply them in order
python manage.py makemigrations
python manage.py migrate
