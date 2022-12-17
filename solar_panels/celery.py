from __future__ import absolute_import
import os
import ssl
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "solar_panels.settings")

app = Celery(
    "solar_panels", 
    broker=settings.BROKER_URL, 
    backend=settings.BACKEND_URL
)
#app = Celery('solar_panels', broker=os.environ['REDIS_URL'])


app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json']
)

app.config_from_object("django.conf:settings")

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)