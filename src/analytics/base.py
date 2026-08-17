from abc import ABC,abstractmethod
class AnalyticsProvider(ABC):
 @abstractmethod
 def snapshot(self,video_id:str)->dict:...
