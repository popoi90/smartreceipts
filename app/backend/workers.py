from celery import Celery
import os

# Create Celery instance
celery_app = Celery(
    "receipt-processor",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
)

@celery_app.task
def test_task():
    return {"status": "Celery is working!"}