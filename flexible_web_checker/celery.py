import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flexible_web_checker.settings")

app = Celery("flexible_web_checker")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


# Celery Beat設定
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
