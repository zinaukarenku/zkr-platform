import os
import celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zkr.settings')

app = celery.Celery('zkr')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
