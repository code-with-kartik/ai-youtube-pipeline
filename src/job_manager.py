from __future__ import annotations
import re
from pathlib import Path
from uuid import uuid4
from src.config import load_settings
from src.constants import STAGES
from src.io_utils import atomic_write_json,load_json,utc_now
from src.state_machine import validate_transition
def jobs_dir(root:Path|None=None)->Path:return (root or load_settings().storage_root)/"jobs"
def job_dir(job_id:str,root:Path|None=None)->Path:
    if not re.fullmatch(r"JOB_\d{6}",job_id):raise ValueError("invalid job id")
    return jobs_dir(root)/job_id
def create_job(topic:str,root:Path|None=None)->dict:
    topic=topic.strip()
    if not topic:raise ValueError("Topic cannot be empty")
    base=jobs_dir(root);base.mkdir(parents=True,exist_ok=True); nums=[int(m.group(1)) for p in base.iterdir() if p.is_dir() and (m:=re.fullmatch(r"JOB_(\d{6})",p.name))]
    jid=f"JOB_{max(nums,default=0)+1:06d}";directory=base/jid;directory.mkdir()
    for folder in ("research","script","voice","visuals","subtitles","render","reports","thumbnail","metadata","analytics","archive"): (directory/folder).mkdir()
    now=utc_now();job={"schema_version":1,"job_id":jid,"uuid":str(uuid4()),"topic":topic,"created_at":now,"updated_at":now,"status":"CREATED","current_stage":"research","attempts":{s:0 for s in STAGES},"pipeline":{s:"PENDING" for s in STAGES},"errors":[],"artifacts":{},"publication":{"video_id":None,"published_at":None,"cleanup_eligible_at":None},"analytics_references":[]}
    atomic_write_json(directory/"job.json",job);return job
def load_job(job_id:str,root:Path|None=None)->dict:return load_json(job_dir(job_id,root)/"job.json")
def save_job(job:dict,root:Path|None=None)->None:job["updated_at"]=utc_now();atomic_write_json(job_dir(job["job_id"],root)/"job.json",job)
def transition(job:dict,stage:str,target:str,root:Path|None=None,force:bool=False)->None:
    if stage not in job["pipeline"]:raise ValueError(f"unknown stage {stage}")
    validate_transition(job["pipeline"][stage],target,force=force);job["pipeline"][stage]=target;job["current_stage"]=stage;job["status"]="BLOCKED" if target=="BLOCKED" else ("FAILED" if target=="FAILED" else "RUNNING")
    if target=="RUNNING":job["attempts"][stage]=job["attempts"].get(stage,0)+1
    save_job(job,root)
def list_jobs(root:Path|None=None)->list[dict]:
    base=jobs_dir(root)
    if not base.exists():return []
    return [load_json(p) for p in sorted(base.glob("JOB_??????/job.json"))]

