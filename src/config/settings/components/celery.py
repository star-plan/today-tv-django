import os

from celery.schedules import crontab

# Docker Compose 已提供 Redis；允许部署环境通过变量替换为托管 Redis 或 RabbitMQ。
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')

# Celery Configuration Options
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# Configure Celery to use backend
CELERY_CACHE_BACKEND = 'django-cache'

# 每日节目播出后同步一次。运维方可通过环境变量调整播出时间，不需要改动业务代码。
CELERY_BEAT_SCHEDULE = {
    'sync-today-tv-nightly': {
        'task': 'television.sync_today_tv',
        'schedule': crontab(
            hour=os.environ.get('TODAY_TV_SYNC_HOUR', '23'),
            minute=os.environ.get('TODAY_TV_SYNC_MINUTE', '15'),
        ),
        'kwargs': {'pages': int(os.environ.get('TODAY_TV_CRAWL_PAGES', '3'))},
    },
}
