from abc import ABC,abstractmethod
from pathlib import Path
class Storage(ABC):
 @abstractmethod
 def put(self,source:Path,key:str)->str:...
