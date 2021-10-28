import os
from celery import Celery


CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL'),
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')

print("worker CELERY_BROKER_URL", CELERY_BROKER_URL)
print("worker CELERY_RESULT_BACKEND", CELERY_RESULT_BACKEND)

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
