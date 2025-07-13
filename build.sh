#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Only collect static files if not disabled
if [ "$DISABLE_COLLECTSTATIC" != "1" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

echo "Build completed successfully!"