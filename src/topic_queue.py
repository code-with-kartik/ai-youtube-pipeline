from __future__ import annotations
from pathlib import Path
from src.config import load_settings
from src.io_utils import atomic_write_json, load_json, utc_now
def queue_file(root: Path | None=None)->Path: return (root or load_settings().storage_root)/"topics"/"queue.json"
def _load_queue(root: Path | None=None)->list[dict]:
    path=queue_file(root)
    if not path.exists(): return []
    try: data=load_json(path)
    except Exception as exc: raise RuntimeError(f"Topic queue is corrupted: {path}") from exc
    if not isinstance(data,list): raise RuntimeError("Topic queue must contain a JSON list")
    return [{"topic":x,"priority":0,"added_at":utc_now()} if isinstance(x,str) else x for x in data]
def _save_queue(queue:list[dict],root:Path|None=None)->None: atomic_write_json(queue_file(root),queue)
def add_topic(topic:str,priority:int=0,root:Path|None=None)->dict:
    topic=topic.strip()
    if not topic: raise ValueError("Topic cannot be empty")
    item={"topic":topic,"priority":int(priority),"added_at":utc_now()}; q=_load_queue(root); q.append(item); _save_queue(q,root); return item
def list_topics(root:Path|None=None)->list[dict]: return _load_queue(root)
def peek_next_topic(root:Path|None=None)->dict|None:
    q=_load_queue(root); return sorted(enumerate(q),key=lambda x:(-int(x[1].get("priority",0)),x[0]))[0][1] if q else None
def consume_next_topic(root:Path|None=None)->dict|None:
    q=_load_queue(root)
    if not q:return None
    i=sorted(range(len(q)),key=lambda n:(-int(q[n].get("priority",0)),n))[0]; item=q.pop(i); _save_queue(q,root); return item
def get_next_topic(root:Path|None=None)->str|None:
    item=consume_next_topic(root); return item["topic"] if item else None
