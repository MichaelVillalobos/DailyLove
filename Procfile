web: gunicorn --access-logfile=- --error-logfile=- --bind=0.0.0.0:8000 --workers=1 --timeout=120 --reload app:create_app()