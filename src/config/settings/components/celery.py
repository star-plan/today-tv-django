CELERY_BROKER_URL = 'pyamqp://localhost:5672'
CELERY_RESULT_BACKEND = 'rpc://'

# Celery Configuration Options
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# Configure Celery to use backend
CELERY_CACHE_BACKEND = 'django-cache'
