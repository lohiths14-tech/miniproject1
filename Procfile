web: gunicorn "app:create_app()" --bind 0.0.0.0:$PORT
worker: celery -A app.celery worker --loglevel=info
