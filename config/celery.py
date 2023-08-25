from __future__ import absolute_import, unicode_literals

import os
from celery.schedules import crontab
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config', broker=f'pyamqp://guest@rabbit:5672')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'print-message-ten-seconds': {
        'task': 'update_costs',
        'schedule': crontab(minute='*/1'),
    }
}