from __future__ import annotations
import shutil
from datetime import datetime,timezone
from pathlib import Path
TEMP_DIRS={"voice","visuals","subtitles","render"}
def cleanup_job(job_dir:Path,job:dict,*,dry_run:bool=True,now:datetime|None=None)->dict:
 root=job_dir.parent.resolve();target=job_dir.resolve();now=now or datetime.now(timezone.utc);eligible=job.get("publication",{}).get("cleanup_eligible_at")
 expected=job.get("job_id")
 if root not in target.parents or target==root or target.is_symlink() or not expected or target.name!=expected:raise ValueError("unsafe cleanup path")
 if not job.get("publication",{}).get("published_at") or not eligible:return {"decision":"SKIP","reason":"not published/eligible","paths":[]}
 if now<datetime.fromisoformat(eligible):return {"decision":"SKIP","reason":"retention active","paths":[]}
 paths=[]
 for name in TEMP_DIRS:
  path=target/name
  if path.exists() and not path.is_symlink():paths.append(str(path));
  if path.exists() and not dry_run and not path.is_symlink():shutil.rmtree(path);path.mkdir()
 return {"decision":"DRY_RUN" if dry_run else "COMPLETED","paths":paths}
