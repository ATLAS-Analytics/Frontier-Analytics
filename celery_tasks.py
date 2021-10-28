import os
from celery import Celery
from FrontierData.DataExtraction.loadEsData import *
from FrontierData.CachingEfficiency import *
from FrontierData.Config.settings import *


CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL'),
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')

print("tasks CELERY_BROKER_URL", CELERY_BROKER_URL)
print("tasks CELERY_RESULT_BACKEND", CELERY_RESULT_BACKEND)

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND, redis_socket_connect_timeout=60)
config_variable = os.environ.get('CONFIG_FILE')


@celery.task(bind=True, name='tasks.extract')
def extractESdata(self, param, parquet_path):
    setg = Settings(config_variable)
    path = parquet_path + '/' + param["parquetname"]
    extractElasticSearchData(param['Task_id'], param['Since'], param['Until'], param['Cached'], path, setg, self)


@celery.task(bind=True, name='tasks.stop')
def stopExtraction(self, task_id):
    celery.control.revoke(task_id, terminate=True)


@celery.task(bind=True, name='tasks.caching_efficiency')
def calculate_caching_efficiency(self, path, folders):
    setg = Settings(config_variable)
    results = calculateCachingEfficiency(path, folders, setg)
    return results
