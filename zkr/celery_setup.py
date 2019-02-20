import os
import celery
from ddtrace import patch

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zkr.settings')

patch(celery=True)
app = celery.Celery('zkr')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
