import os
from celery import Celery


CELERY_URL = os.environ.get('CELERY_URL')

print("worker CELERY_URL", CELERY_URL)

celery = Celery('tasks', broker=CELERY_URL, backend=CELERY_URL)
