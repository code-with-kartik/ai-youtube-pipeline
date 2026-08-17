import shutil
from pathlib import Path
from src.storage.base import Storage
class LocalStorage(Storage):
 def __init__(self,root:Path):self.root=root.resolve()
 def put(self,source:Path,key:str)->str:
  target=(self.root/key).resolve()
  if self.root not in target.parents:raise ValueError("path traversal")
  target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);return str(target)

