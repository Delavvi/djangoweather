from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import schedule
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoweather.settings.local')
app = Celery('celery')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'Send_mail_to_Client': {
        'task': 'weather.tasks.send_emails',
        'schedule': schedule(3600.0),
    }
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')