#!/usr/bin/env bash
# start.sh

# Exit on error
set -o errexit

echo "🚀 Starting deployment script..."
echo "📂 Current directory: $(pwd)"
echo "🐍 Python version: $(python --version)"

# Check if migrations are needed (optional, uncomment if using Flask-Migrate)
# echo "🗄️  Running database migrations..."
# flask db upgrade

echo "🔥 Starting Gunicorn..."
# Start Gunicorn with the WSGI entry point
exec gunicorn wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile -
