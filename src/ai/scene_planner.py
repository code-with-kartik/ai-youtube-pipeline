def plan_scenes(script:dict)->dict:
 scenes=[]
 for i,section in enumerate(script["sections"],1):
  text=section["text"];duration=max(2.0,len(text.split())/2.5);scenes.append({"scene_id":f"SCENE_{i:03d}","start_order":i,"voice_text":text,"subtitle_text":text,"estimated_duration":round(duration,2),"visual_description":f"Clean educational illustration for {section['name']}","visual_prompt":f"Educational graphic about {script['topic']}, {section['name']}","asset_type":"image","transition":"fade","importance":"high" if i==1 else "normal","source_reference":script.get("claim_references",[])})
 return {"job_id":script["job_id"],"scenes":scenes}

