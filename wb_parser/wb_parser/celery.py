import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wb_parser.settings')

app = Celery('wb_parser')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
