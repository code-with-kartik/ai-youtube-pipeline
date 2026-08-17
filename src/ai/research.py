from src.io_utils import utc_now
from src.providers import ResearchProvider
class MockResearchProvider(ResearchProvider):
 def research(self,job:dict)->dict:
  topic=job["topic"]
  return {"job_id":job["job_id"],"topic":topic,"summary":f"A concise educational overview of {topic}.","key_points":[f"{topic} can be explained through observable principles.","Reliable explanations distinguish evidence from uncertainty."],"claims":[{"claim_id":"CLAIM_001","text":f"This video presents an introductory explanation of {topic}.","source_ids":[],"status":"SUPPORTED_BY_SCOPE"}],"sources":[],"uncertainties":["Mock research does not perform external source verification."],"provider":"mock","generated_at":utc_now()}
def validate_research(data:dict)->None:
 for key,typ in {"job_id":str,"topic":str,"summary":str,"key_points":list,"claims":list,"sources":list,"uncertainties":list,"generated_at":str}.items():
  if key not in data or not isinstance(data[key],typ):raise ValueError(f"invalid research field: {key}")

