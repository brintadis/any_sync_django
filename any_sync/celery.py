import os
from celery import Celery

# Set the default django settings for celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'any_sync.settings')

# Init Celery application
app = Celery('any_sync')

# Read configuration from django settings:
#   namespace='CELERY' means that config string should start with CELERY_.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover task modules.
# Searches a list of packages for a "tasks.py" module.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
