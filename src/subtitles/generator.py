from pathlib import Path
def stamp(value:float)->str:
 ms=round(value*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
def generate_srt(scenes:list[dict],path:Path)->dict:
 cursor=0.0;lines=[];entries=[]
 for i,s in enumerate(scenes,1):
  end=cursor+float(s["estimated_duration"]);lines += [str(i),f"{stamp(cursor)} --> {stamp(end)}",s["subtitle_text"],""];entries.append({"start":cursor,"end":end});cursor=end
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text("\n".join(lines),encoding="utf-8");return {"decision":"PASS","entries":entries,"duration":cursor,"encoding":"utf-8","problems":[]}

