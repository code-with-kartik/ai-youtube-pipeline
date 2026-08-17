from abc import ABC,abstractmethod
from pathlib import Path
class ThumbnailProvider(ABC):
 @abstractmethod
 def generate(self,topic:str,output:Path,width:int,height:int)->dict:...
