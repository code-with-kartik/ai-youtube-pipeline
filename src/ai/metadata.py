def generate_metadata(job:dict,script:dict,language:str,privacy:str)->dict:
 title=job["topic"].strip()[:100]
 return {"title":title,"description":f"An educational overview of {job['topic']}.\n\nGenerated with a reviewed automation workflow.","tags":[w.lower().strip(".,") for w in title.split()[:8]],"category_id":"27","language":language,"privacy_status":privacy,"publish_at":None}
def validate_metadata(data:dict)->None:
 if not isinstance(data.get("title"),str) or not data["title"].strip() or len(data["title"])>100:raise ValueError("invalid title")
 if not isinstance(data.get("description"),str) or not data["description"].strip():raise ValueError("invalid description")
 if data.get("privacy_status") not in {"private","unlisted","public"}:raise ValueError("invalid privacy")
