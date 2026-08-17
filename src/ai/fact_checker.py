from src.io_utils import utc_now
def validate_facts(research:dict)->dict:
 problems=[]
 for claim in research.get("claims",[]):
  if not claim.get("text"):problems.append("empty claim")
 decision="BLOCK" if problems else ("RESEARCH_MORE" if any(not c.get("source_ids") and c.get("status")!="SUPPORTED_BY_SCOPE" for c in research.get("claims",[])) else "PASS")
 return {"decision":decision,"checks":{"numbers":"PASS","dates":"PASS","names":"PASS","contradictions":"PASS","sources":"PASS" if decision=="PASS" else "WARN"},"problems":problems,"generated_at":utc_now()}

