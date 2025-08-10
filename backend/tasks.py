from celery import Celery
import shutil
import os

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task
def cleanup_directory(dir_path: str):
    """
    rm -rf the specified directory. CAREFUL when you call this.
    """
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        shutil.rmtree(dir_path)
        print(f"Deleted directory: {dir_path}")
    else:
        print(f"Directory not found: {dir_path}")

@celery_app.task
def add(x, y):
    return x + y