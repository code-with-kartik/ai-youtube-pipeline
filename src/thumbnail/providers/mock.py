from pathlib import Path
from src.media import probe,run
class MockThumbnailProvider:
 def generate(self,topic:str,output:Path,width:int=1280,height:int=720)->dict:
  output.parent.mkdir(parents=True,exist_ok=True);run(["ffmpeg","-y","-f","lavfi","-i",f"color=c=#264653:s={width}x{height}","-frames:v","1",str(output)]);return {"provider":"mock","file_path":str(output),"dimensions":f"{width}x{height}","status":"COMPLETED"}
def validate_thumbnail(path:Path,width:int,height:int)->dict:
 try:
  stream=probe(path)["streams"][0];ok=path.suffix.lower() in {".jpg",".jpeg",".png"} and stream.get("width")==width and stream.get("height")==height
 except Exception:ok=False
 return {"decision":"PASS" if ok else "BLOCK","file_exists":path.is_file(),"dimensions":f"{width}x{height}" if ok else "invalid"}

