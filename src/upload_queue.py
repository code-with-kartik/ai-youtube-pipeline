from pathlib import Path
from src.checks.final_checker import validate_final_report
from src.io_utils import atomic_write_json,load_json,utc_now
def queue_path(root:Path)->Path:return root/"upload_queue.json"
def load_queue(root:Path)->list[dict]:
 p=queue_path(root);return load_json(p) if p.exists() else []
def enqueue(job:dict,job_dir:Path,root:Path)->dict:
 report=load_json(job_dir/"reports"/"final_checker.json")
 if not validate_final_report(report) or report["decision"]!="PASS":raise ValueError("only valid PASS jobs may enter upload queue")
 q=load_queue(root);existing=next((x for x in q if x["job_id"]==job["job_id"]),None)
 if existing:return existing
 item={"job_id":job["job_id"],"video":str(job_dir/"render"/"final.mp4"),"thumbnail":str(job_dir/"thumbnail"/"thumbnail.jpg"),"metadata":str(job_dir/"metadata"/"metadata.json"),"approval_report":str(job_dir/"reports"/"final_checker.json"),"requested_publish_time":None,"status":"QUEUED","retry_count":0,"created_at":utc_now()};q.append(item);atomic_write_json(queue_path(root),q);return item

