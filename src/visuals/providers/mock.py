from pathlib import Path
from src.media import run
from src.providers import VisualProvider
class MockVisualProvider(VisualProvider):
 def generate(self,scene:dict,output:Path,width:int,height:int)->dict:
  output.parent.mkdir(parents=True,exist_ok=True);color=["#14213d","#1b4332","#3c096c"][((scene["start_order"]-1)%3)]
  run(["ffmpeg","-y","-f","lavfi","-i",f"color=c={color}:s={width}x{height}","-frames:v","1",str(output)])
  return {"provider":"mock","status":"COMPLETED","file_path":str(output),"license":"synthetic/local"}

