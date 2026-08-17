from __future__ import annotations
import argparse,json
from datetime import datetime,timezone
from src.config import load_settings
from src.doctor import run_doctor
from src.job_manager import create_job,list_jobs,load_job
from src.pipeline import publish_job,queue_for_upload,run_job
from src.storage.archive import archive_job
from src.storage.cleanup import cleanup_job
from src.topic_queue import add_topic,consume_next_topic,list_topics,peek_next_topic
def emit(value):print(json.dumps(value,indent=2,default=str))
def main():
 parser=argparse.ArgumentParser(prog="ai-youtube",description="Resumable AI YouTube production pipeline");sub=parser.add_subparsers(dest="command",required=True)
 p=sub.add_parser("add-topic");p.add_argument("topic");p.add_argument("--priority",type=int,default=0)
 sub.add_parser("list-topics");sub.add_parser("peek-topic");sub.add_parser("run-next")
 p=sub.add_parser("run-job");p.add_argument("job_id");p.add_argument("--force-stage")
 sub.add_parser("resume");p=sub.add_parser("status");p.add_argument("job_id");sub.add_parser("status-all")
 for name in ("validate","render","final-check"):
  p=sub.add_parser(name);p.add_argument("job_id")
 p=sub.add_parser("queue-upload");p.add_argument("job_id");p=sub.add_parser("publish");p.add_argument("job_id")
 p=sub.add_parser("cleanup");p.add_argument("job_id");p.add_argument("--execute",action="store_true")
 p=sub.add_parser("archive");p.add_argument("job_id")
 p=sub.add_parser("analytics");p.add_argument("job_id")
 sub.add_parser("doctor")
 args=parser.parse_args();settings=load_settings();root=settings.storage_root
 if args.command=="add-topic":emit(add_topic(args.topic,args.priority,root))
 elif args.command=="list-topics":emit(list_topics(root))
 elif args.command=="peek-topic":emit(peek_next_topic(root))
 elif args.command=="run-next":
  item=consume_next_topic(root)
  if not item:emit({"status":"EMPTY"})
  else:
   job=create_job(item["topic"],root);emit(run_job(job["job_id"],settings))
 elif args.command=="run-job":emit(run_job(args.job_id,settings,args.force_stage))
 elif args.command=="resume":
  results=[]
  for job in list_jobs(root):
   if job.get("status") not in {"READY_TO_UPLOAD","PUBLISHED","DRY_RUN_COMPLETE","BLOCKED"}:
    try:results.append(run_job(job["job_id"],settings))
    except Exception as exc:results.append({"job_id":job["job_id"],"error":str(exc)})
  emit(results)
 elif args.command=="status":emit(load_job(args.job_id,root))
 elif args.command=="status-all":emit(list_jobs(root))
 elif args.command in {"validate","render","final-check"}:emit(run_job(args.job_id,settings,"technical_qc" if args.command=="validate" else ("render" if args.command=="render" else "final_checker")))
 elif args.command=="queue-upload":emit(queue_for_upload(args.job_id,settings))
 elif args.command=="publish":emit(publish_job(args.job_id,settings))
 elif args.command=="cleanup":
  job=load_job(args.job_id,root);emit(cleanup_job(root/"jobs"/args.job_id,job,dry_run=not args.execute))
 elif args.command=="archive":emit(archive_job(root/"jobs"/args.job_id))
 elif args.command=="analytics":emit({"status":"CREDENTIALS_REQUIRED","job_id":args.job_id})
 elif args.command=="doctor":emit(run_doctor(settings))
if __name__=="__main__":main()

