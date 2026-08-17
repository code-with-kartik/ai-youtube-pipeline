from src.constants import MANDATORY_FINAL_CHECKS
VALID_DECISIONS={"PASS","REGENERATE","BLOCK"}
def validate_final_report(report:object,min_confidence:float=.8)->bool:
 if not isinstance(report,dict) or report.get("decision") not in VALID_DECISIONS:return False
 if not isinstance(report.get("checks"),dict) or not MANDATORY_FINAL_CHECKS.issubset(report["checks"]):return False
 if not all(isinstance(report.get(k),list) for k in ("problems","required_fixes","affected_stages")):return False
 confidence=report.get("confidence")
 return isinstance(confidence,(int,float)) and 0<=confidence<=1 and (report["decision"]!="PASS" or confidence>=min_confidence)
def final_check(inputs:dict)->dict:
 checks={"research":"PASS" if inputs.get("research") else "BLOCK","facts":inputs.get("facts",{}).get("decision","BLOCK"),"script":inputs.get("script_validation",{}).get("decision","BLOCK"),"technical":inputs.get("technical",{}).get("decision","BLOCK"),"metadata":"PASS" if inputs.get("metadata_valid") else "BLOCK","thumbnail":"PASS" if inputs.get("thumbnail_valid") else "BLOCK","policy":"PASS" if inputs.get("policy_valid",False) else "BLOCK"}
 problems=[f"{k}: {v}" for k,v in checks.items() if v!="PASS"];decision="PASS" if not problems else ("REGENERATE" if any(v=="REGENERATE" for v in checks.values()) else "BLOCK")
 return {"decision":decision,"checks":checks,"problems":problems,"required_fixes":problems,"affected_stages":[k for k,v in checks.items() if v!="PASS"],"confidence":1.0 if decision=="PASS" else 0.0}
