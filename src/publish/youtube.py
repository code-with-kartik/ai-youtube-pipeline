from __future__ import annotations
from pathlib import Path
from src.checks.final_checker import validate_final_report
from src.io_utils import load_json
class UploadBlocked(RuntimeError):pass
class YouTubePublisher:
 def __init__(self,job_dir:Path,client_secrets:str="",token_file:str="",upload_callable=None):self.job_dir,self.client_secrets,self.token_file,self.upload_callable=job_dir,client_secrets,token_file,upload_callable
 def publish(self,job:dict)->dict:
  report_path=self.job_dir/"reports"/"final_checker.json"
  try:report=load_json(report_path)
  except Exception as exc:raise UploadBlocked("missing or malformed Final Checker report") from exc
  if not validate_final_report(report) or report["decision"]!="PASS":raise UploadBlocked("production upload requires schema-valid Final Checker PASS")
  for p in (self.job_dir/"render"/"final.mp4",self.job_dir/"thumbnail"/"thumbnail.jpg",self.job_dir/"metadata"/"metadata.json"):
   if not p.is_file():raise UploadBlocked(f"missing required upload asset: {p.name}")
  if job.get("publication",{}).get("video_id"):return {"status":"ALREADY_PUBLISHED","video_id":job["publication"]["video_id"]}
  if not self.client_secrets or not self.token_file:raise UploadBlocked("YouTube credentials are not configured")
  if self.upload_callable is None:raise UploadBlocked("YouTube API adapter dependency is not installed/configured")
  return self.upload_callable(job,self.job_dir)

