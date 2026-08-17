from __future__ import annotations
import json,shutil,sys
from pathlib import Path
from src.config import Settings
def run_doctor(settings:Settings)->dict:
 checks=[]
 def add(name,status,detail):checks.append({"name":name,"status":status,"detail":detail})
 add("python","PASS" if sys.version_info>=(3,11) else "FAIL",sys.version.split()[0])
 for binary in ("ffmpeg","ffprobe"):add(binary,"PASS" if shutil.which(binary) else "FAIL",shutil.which(binary) or "not found")
 try:settings.validate();add("configuration","PASS","valid")
 except Exception as exc:add("configuration","FAIL",str(exc))
 try:settings.storage_root.mkdir(parents=True,exist_ok=True);probe=settings.storage_root/".doctor";probe.write_text("ok");probe.unlink();add("storage","PASS",str(settings.storage_root))
 except Exception as exc:add("storage","FAIL",str(exc))
 for file in settings.storage_root.glob("jobs/JOB_??????/job.json"):
  try:json.loads(file.read_text(encoding="utf-8"))
  except Exception as exc:add("state_integrity","FAIL",f"{file}: {exc}");break
 else:add("state_integrity","PASS","job JSON readable")
 ready=bool(settings.youtube_client_secrets and settings.youtube_token_file)
 add("youtube_credentials","PASS" if ready else "WARN","configured" if ready else "not configured; dry-run only")
 overall="FAIL" if any(x["status"]=="FAIL" for x in checks) else ("WARN" if any(x["status"]=="WARN" for x in checks) else "PASS")
 return {"overall":overall,"checks":checks}

