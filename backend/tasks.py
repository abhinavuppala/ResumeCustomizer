from celery import Celery
import shutil
import os
from dotenv import load_dotenv

load_dotenv()
assert os.getenv("REDIS_URL"), "Missing REDIS_URL environment variable"
celery_app = Celery(
    "worker",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL")
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