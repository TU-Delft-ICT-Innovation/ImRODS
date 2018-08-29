# coding=UTF8
from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tuirods.settings")

app = Celery('tuirods')
TIMEZONE = 'Europe/Amsterdam'
CELERY_TIMEZONE = 'Europe/Amsterdam'

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'create-thumbs': {
        'task': 'irodsapp.tasks.create_thumbnails',
        'schedule': crontab(minute=00, hour='0'),
    },
}
