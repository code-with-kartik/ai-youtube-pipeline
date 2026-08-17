from __future__ import annotations
import json,subprocess
from pathlib import Path
def run(command:list[str],timeout:int=120)->subprocess.CompletedProcess:
 return subprocess.run(command,check=True,capture_output=True,text=True,timeout=timeout)
def probe(path:Path)->dict:
 result=run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(path)]);return json.loads(result.stdout)
def duration(path:Path)->float:return float(probe(path)["format"]["duration"])

