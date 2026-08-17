import time
from src.config import load_settings
from src.job_manager import create_job
from src.pipeline import run_job
from src.topic_queue import consume_next_topic
def worker(once:bool=False,interval:int=300):
 settings=load_settings()
 while True:
  item=consume_next_topic(settings.storage_root)
  if item:run_job(create_job(item["topic"],settings.storage_root)["job_id"],settings)
  if once:return
  time.sleep(max(30,interval))

