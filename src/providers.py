from __future__ import annotations
from abc import ABC,abstractmethod
from pathlib import Path
class ResearchProvider(ABC):
 @abstractmethod
 def research(self,job:dict)->dict:...
class VoiceProvider(ABC):
 @abstractmethod
 def generate(self,text:str,output:Path,duration:float)->dict:...
class VisualProvider(ABC):
 @abstractmethod
 def generate(self,scene:dict,output:Path,width:int,height:int)->dict:...
class Publisher(ABC):
 @abstractmethod
 def publish(self,job:dict)->dict:...

