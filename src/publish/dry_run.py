from src.io_utils import utc_now
class DryRunPublisher:
 def publish(self,job:dict)->dict:return {"status":"DRY_RUN","video_id":f"dry-{job['job_id'].lower()}","published_at":utc_now(),"external_call":False}

