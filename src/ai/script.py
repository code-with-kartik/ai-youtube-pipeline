from src.io_utils import utc_now
def generate_script(job:dict,research:dict,target_duration:float,style:str,language:str)->dict:
 points=" ".join(research["key_points"])
 sections=[{"name":"hook","text":f"What makes {job['topic']} worth understanding?"},{"name":"body","text":points},{"name":"ending","text":f"That is the essential idea behind {job['topic']}."}]
 return {"job_id":job["job_id"],"topic":job["topic"],"language":language,"style":style,"target_duration":target_duration,"sections":sections,"claim_references":[c["claim_id"] for c in research["claims"]],"generated_at":utc_now()}
def script_text(script:dict)->str:return "\n\n".join(s["text"] for s in script["sections"])

