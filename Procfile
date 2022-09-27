web: gunicorn solar_panels.wsgi
celery: celery -A solar_panels.celery worker -l info
celerybeat: celery -A solar_panels beat -l INFO 
celeryworker2: celery -A solar_panels.celery worker & celery -A solar_panels beat -l INFO & wait -n