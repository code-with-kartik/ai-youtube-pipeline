from __future__ import annotations
import shutil
from pathlib import Path
PRESERVE=("render/final.mp4","thumbnail/thumbnail.jpg","script/script.json","script/script.txt","metadata/metadata.json","research/research.json","reports/fact_validation.json","reports/script_validation.json","reports/technical_qc.json","reports/final_checker.json","reports/publication.json","reports/checksums.json")
def archive_job(job_dir:Path)->dict:
 target=job_dir/"archive";target.mkdir(exist_ok=True);copied=[]
 for relative in PRESERVE:
  source=job_dir/relative
  if source.is_file():dest=target/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest);copied.append(relative)
 return {"decision":"COMPLETED","files":copied}

