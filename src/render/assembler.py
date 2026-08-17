from __future__ import annotations
import json
from pathlib import Path
from src.media import run
def render_video(images:list[Path],scenes:list[dict],voice:Path,subtitles:Path,output:Path,width:int,height:int,fps:int,burn:bool=True)->dict:
 work=output.parent;clips=[];commands=[]
 for i,(image,scene) in enumerate(zip(images,scenes),1):
  clip=work/f"clip_{i:03d}.mp4";cmd=["ffmpeg","-y","-loop","1","-i",str(image),"-t",str(scene["estimated_duration"]),"-vf",f"scale={width}:{height},format=yuv420p","-r",str(fps),"-c:v","libx264",str(clip)];run(cmd);commands.append(cmd);clips.append(clip)
 concat=work/"concat.txt";concat.write_text("".join(f"file '{p.resolve()}'\n" for p in clips),encoding="utf-8");merged=work/"video_only.mp4";run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(merged)])
 vf=f"subtitles={str(subtitles).replace(':','\\:')}" if burn else "null";cmd=["ffmpeg","-y","-i",str(merged),"-i",str(voice),"-vf",vf,"-c:v","libx264","-c:a","aac","-shortest","-movflags","+faststart",str(output)];run(cmd);commands.append(cmd)
 meta={"commands":commands,"output":str(output)};(work/"render_metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8");return meta

