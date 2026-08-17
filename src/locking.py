from __future__ import annotations
import json, os, socket, time
from pathlib import Path
class LockBusy(RuntimeError): pass
class JobLock:
    def __init__(self, path: Path, stale_seconds: int = 3600): self.path, self.stale_seconds, self.acquired = path, stale_seconds, False
    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True); payload={"pid":os.getpid(),"host":socket.gethostname(),"created":time.time()}
        try: fd=os.open(self.path, os.O_CREAT|os.O_EXCL|os.O_WRONLY, 0o600)
        except FileExistsError:
            try: existing=json.loads(self.path.read_text(encoding="utf-8"))
            except Exception: existing={}
            age=time.time()-float(existing.get("created",time.time())); pid=int(existing.get("pid",-1)); alive=existing.get("host")==socket.gethostname() and pid>0 and Path(f"/proc/{pid}").exists()
            if alive or age < self.stale_seconds: raise LockBusy(f"job locked by pid {pid}")
            self.path.unlink(missing_ok=True); fd=os.open(self.path, os.O_CREAT|os.O_EXCL|os.O_WRONLY, 0o600)
        with os.fdopen(fd,"w",encoding="utf-8") as f: json.dump(payload,f)
        self.acquired=True; return self
    def __exit__(self,*_):
        if self.acquired: self.path.unlink(missing_ok=True)
