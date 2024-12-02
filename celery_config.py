from celery import Celery

celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',  # Redis as the broker
    backend='redis://localhost:6379/0', # Redis as the result backend
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
)
