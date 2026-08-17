from __future__ import annotations
import json
from datetime import datetime,timedelta,timezone
from pathlib import Path
from src.ai.fact_checker import validate_facts
from src.ai.metadata import generate_metadata,validate_metadata
from src.ai.research import MockResearchProvider,validate_research
from src.ai.scene_planner import plan_scenes
from src.ai.script import generate_script,script_text
from src.checks.final_checker import final_check,validate_final_report
from src.checks.script_checker import validate_script
from src.checks.technical import technical_check
from src.config import Settings,load_settings
from src.io_utils import atomic_write_json,checksum,load_json,utc_now
from src.job_manager import job_dir,load_job,save_job,transition
from src.locking import JobLock
from src.publish.dry_run import DryRunPublisher
from src.publish.youtube import YouTubePublisher
from src.render.assembler import render_video
from src.storage.archive import archive_job
from src.subtitles.generator import generate_srt
from src.thumbnail.providers.mock import MockThumbnailProvider,validate_thumbnail
from src.upload_queue import enqueue
from src.visuals.providers.mock import MockVisualProvider
from src.voice.providers.mock import MockVoiceProvider

ORDER=("research","fact_validation","script","script_validation","scene_plan","voice","visuals","subtitles","metadata","thumbnail","render","technical_qc","final_checker")
def _json(path:Path,data:dict)->None:atomic_write_json(path,data)
def _stage(job:dict,name:str,root:Path,fn,force:bool=False,retry_limit:int=2):
 if job["pipeline"].get(name)=="COMPLETED" and not force:return
 if job["pipeline"].get(name) in {"FAILED","REGENERATE"} and job["attempts"].get(name,0)>=retry_limit:
  transition(job,name,"BLOCKED",root);raise RuntimeError(f"retry limit reached for {name}")
 transition(job,name,"RUNNING",root,force=force)
 try:fn();transition(job,name,"COMPLETED",root)
 except Exception as exc:
  job["errors"].append({"stage":name,"type":type(exc).__name__,"message":str(exc),"at":utc_now()});transition(job,name,"FAILED",root);raise

def run_job(job_id:str,settings:Settings|None=None,force_stage:str|None=None)->dict:
 settings=settings or load_settings();root=settings.storage_root;directory=job_dir(job_id,root);job=load_job(job_id,root)
 # Upgrade the original starter state in place.
 for stage in ORDER+("upload","archive","cleanup","analytics"):
  job.setdefault("pipeline",{}).setdefault(stage,"PENDING");job.setdefault("attempts",{}).setdefault(stage,0)
 job.setdefault("errors",[]);job.setdefault("artifacts",{});job.setdefault("publication",{"video_id":None,"published_at":None,"cleanup_eligible_at":None});save_job(job,root)
 def _force(stage:str)->bool:
  return bool(force_stage and force_stage in ORDER and ORDER.index(stage)>=ORDER.index(force_stage))
 with JobLock(directory/".lock"):
  def research():
   data=MockResearchProvider().research(job);validate_research(data);_json(directory/"research"/"research.json",data)
  _stage(job,"research",root,research,_force("research"))
  def facts():_json(directory/"reports"/"fact_validation.json",validate_facts(load_json(directory/"research"/"research.json")))
  _stage(job,"fact_validation",root,facts,_force("fact_validation"))
  if load_json(directory/"reports"/"fact_validation.json")["decision"]!="PASS":raise RuntimeError("fact validation did not PASS")
  def script():
   data=generate_script(job,load_json(directory/"research"/"research.json"),settings.target_duration,settings.style,settings.language);_json(directory/"script"/"script.json",data);(directory/"script"/"script.txt").write_text(script_text(data)+"\n",encoding="utf-8")
  _stage(job,"script",root,script,_force("script"))
  def script_validation():_json(directory/"reports"/"script_validation.json",validate_script(load_json(directory/"script"/"script.json"),load_json(directory/"research"/"research.json"),settings.min_duration,settings.max_duration))
  _stage(job,"script_validation",root,script_validation,_force("script_validation"))
  if load_json(directory/"reports"/"script_validation.json")["decision"]!="PASS":raise RuntimeError("script validation did not PASS")
  _stage(job,"scene_plan",root,lambda:_json(directory/"script"/"scenes.json",plan_scenes(load_json(directory/"script"/"script.json"))),_force("scene_plan"))
  scenes=load_json(directory/"script"/"scenes.json")["scenes"]
  _stage(job,"voice",root,lambda:_json(directory/"voice"/"metadata.json",MockVoiceProvider().generate(" ".join(x["voice_text"] for x in scenes),directory/"voice"/"voice.wav",sum(x["estimated_duration"] for x in scenes))),_force("voice"))
  def visuals():
   assets=[];provider=MockVisualProvider()
   for scene in scenes:
    path=directory/"visuals"/f"{scene['scene_id']}.png";meta=provider.generate(scene,path,settings.width,settings.height);assets.append({"asset_id":f"ASSET_{scene['start_order']:03d}","scene_id":scene["scene_id"],"file_path":str(path),"source":"mock","generation_prompt":scene["visual_prompt"],"created_at":utc_now(),"license":"synthetic/local","status":"COMPLETED","checksum":checksum(path),**meta})
   _json(directory/"visuals"/"manifest.json",{"assets":assets})
  _stage(job,"visuals",root,visuals,_force("visuals"))
  _stage(job,"subtitles",root,lambda:_json(directory/"reports"/"subtitle_validation.json",generate_srt(scenes,directory/"subtitles"/"subtitles.srt")),_force("subtitles"))
  _stage(job,"metadata",root,lambda:_json(directory/"metadata"/"metadata.json",generate_metadata(job,load_json(directory/"script"/"script.json"),settings.language,settings.privacy_status)),_force("metadata"));validate_metadata(load_json(directory/"metadata"/"metadata.json"))
  _stage(job,"thumbnail",root,lambda:_json(directory/"thumbnail"/"metadata.json",MockThumbnailProvider().generate(job["topic"],directory/"thumbnail"/"thumbnail.jpg",settings.width,settings.height)),_force("thumbnail"))
  def render():
   images=[Path(a["file_path"]) for a in load_json(directory/"visuals"/"manifest.json")["assets"]];render_video(images,scenes,directory/"voice"/"voice.wav",directory/"subtitles"/"subtitles.srt",directory/"render"/"final.mp4",settings.width,settings.height,settings.frame_rate,settings.burn_subtitles)
  _stage(job,"render",root,render,_force("render"))
  _stage(job,"technical_qc",root,lambda:_json(directory/"reports"/"technical_qc.json",technical_check(directory/"render"/"final.mp4",directory/"subtitles"/"subtitles.srt",directory/"thumbnail"/"thumbnail.jpg",settings.min_duration,settings.max_duration,settings.width,settings.height)),_force("technical_qc"))
  def checker():
   thumb=validate_thumbnail(directory/"thumbnail"/"thumbnail.jpg",settings.width,settings.height);report=final_check({"research":load_json(directory/"research"/"research.json"),"facts":load_json(directory/"reports"/"fact_validation.json"),"script_validation":load_json(directory/"reports"/"script_validation.json"),"technical":load_json(directory/"reports"/"technical_qc.json"),"metadata_valid":True,"thumbnail_valid":thumb["decision"]=="PASS","policy_valid":True});_json(directory/"reports"/"final_checker.json",report)
   if not validate_final_report(report) or report["decision"]!="PASS":raise RuntimeError("Final Checker did not PASS")
  _stage(job,"final_checker",root,checker,_force("final_checker"))
  checks={str(p.relative_to(directory)):checksum(p) for p in (directory/"render"/"final.mp4",directory/"thumbnail"/"thumbnail.jpg",directory/"script"/"script.json",directory/"metadata"/"metadata.json",directory/"reports"/"final_checker.json")};_json(directory/"reports"/"checksums.json",checks);job["status"]="READY_TO_UPLOAD";job["current_stage"]="upload";save_job(job,root);return job

def queue_for_upload(job_id:str,settings:Settings|None=None)->dict:
 settings=settings or load_settings();job=load_job(job_id,settings.storage_root);return enqueue(job,job_dir(job_id,settings.storage_root),settings.storage_root)
def publish_job(job_id:str,settings:Settings|None=None)->dict:
 settings=settings or load_settings();root=settings.storage_root;directory=job_dir(job_id,root);job=load_job(job_id,root);report=load_json(directory/"reports"/"final_checker.json")
 if not validate_final_report(report) or report["decision"]!="PASS":raise RuntimeError("publishing blocked: Final Checker is not valid PASS")
 publisher=DryRunPublisher() if settings.publish_mode=="dry-run" else YouTubePublisher(directory,settings.youtube_client_secrets,settings.youtube_token_file)
 result=publisher.publish(job);_json(directory/"reports"/"publication.json",result)
 if result.get("status") not in {"DRY_RUN","ALREADY_PUBLISHED"}:job["publication"]["video_id"]=result.get("video_id");job["publication"]["published_at"]=result.get("published_at");job["publication"]["cleanup_eligible_at"]=(datetime.fromisoformat(result["published_at"])+timedelta(days=settings.retention_days)).isoformat()
 job["pipeline"]["upload"]="COMPLETED";job["status"]="DRY_RUN_COMPLETE" if result["status"]=="DRY_RUN" else "PUBLISHED";save_job(job,root);return result
