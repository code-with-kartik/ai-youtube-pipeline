from pathlib import Path
from src.media import duration as media_duration,run
from src.providers import VoiceProvider
class MockVoiceProvider(VoiceProvider):
 def generate(self,text:str,output:Path,duration:float)->dict:
  output.parent.mkdir(parents=True,exist_ok=True);run(["ffmpeg","-y","-f","lavfi","-i","sine=frequency=220:sample_rate=48000","-t",str(max(2,duration)),"-af","volume=0.08","-c:a","pcm_s16le",str(output)])
  return {"provider":"mock","status":"COMPLETED","file_path":str(output),"duration":media_duration(output),"synthetic_tone":True}

