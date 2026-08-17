from pathlib import Path
from src.media import probe
def technical_check(video:Path,subtitle:Path,thumbnail:Path|None,min_duration:float,max_duration:float,width:int,height:int)->dict:
 result={"decision":"BLOCK","video_exists":video.is_file(),"audio_exists":False,"duration_seconds":0.0,"resolution":"","problems":[]}
 if not video.is_file() or video.stat().st_size<1024:result["problems"].append("video missing or too small");return result
 try:
  data=probe(video);streams=data.get("streams",[]);v=next((s for s in streams if s.get("codec_type")=="video"),None);a=next((s for s in streams if s.get("codec_type")=="audio"),None);d=float(data["format"]["duration"]);result.update(audio_exists=a is not None,duration_seconds=d,resolution=f"{v.get('width')}x{v.get('height')}" if v else "")
  if not v:result["problems"].append("missing video stream")
  if not a:result["problems"].append("missing audio stream")
  if not min_duration<=d<=max_duration:result["problems"].append("invalid duration")
  if v and (v.get("width")!=width or v.get("height")!=height):result["problems"].append("invalid resolution")
  if not subtitle.is_file():result["problems"].append("missing subtitles")
  if thumbnail is not None and not thumbnail.is_file():result["problems"].append("missing thumbnail")
 except Exception as exc:result["problems"].append(f"ffprobe failure: {type(exc).__name__}")
 result["decision"]="PASS" if not result["problems"] else "BLOCK";return result

