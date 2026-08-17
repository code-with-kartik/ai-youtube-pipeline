def validate_script(script:dict,research:dict,min_duration:float,max_duration:float)->dict:
 problems=[];names={s.get("name") for s in script.get("sections",[])}
 if script.get("topic")!=research.get("topic"):problems.append("topic mismatch")
 for required in ("hook","body","ending"):
  if required not in names:problems.append(f"missing section: {required}")
 estimate=sum(len(s.get("text","").split()) for s in script.get("sections",[]))/2.5
 if not min_duration<=estimate<=max_duration:problems.append("duration estimate outside configured bounds")
 return {"decision":"PASS" if not problems else "REGENERATE","problems":problems,"estimated_duration":estimate,"required_fixes":problems}

