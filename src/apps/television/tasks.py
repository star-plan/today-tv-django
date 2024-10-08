from apps.television.models import Video
from celery import shared_task
from config.celery import app


@app.task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)


@shared_task
def count_videos():
    return Video.objects.count()
