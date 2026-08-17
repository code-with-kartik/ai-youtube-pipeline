import json,os,tempfile,unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
from src.ai.fact_checker import validate_facts
from src.ai.metadata import validate_metadata
from src.ai.research import MockResearchProvider,validate_research
from src.ai.scene_planner import plan_scenes
from src.ai.script import generate_script
from src.checks.final_checker import final_check,validate_final_report
from src.checks.script_checker import validate_script
from src.io_utils import atomic_write_json,load_json
from src.job_manager import create_job,load_job,transition
from src.locking import JobLock,LockBusy
from src.state_machine import InvalidTransition,validate_transition
from src.topic_queue import add_topic,consume_next_topic,list_topics,peek_next_topic
from src.config import Settings

class CoreTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def test_topic_queue_persistence_priority_and_empty(self):
  self.assertIsNone(consume_next_topic(self.root));add_topic("low",0,self.root);add_topic("high",2,self.root);self.assertEqual(peek_next_topic(self.root)["topic"],"high");self.assertEqual(consume_next_topic(self.root)["topic"],"high");self.assertEqual(list_topics(self.root)[0]["topic"],"low")
 def test_empty_topic_rejected(self):
  with self.assertRaises(ValueError):add_topic("  ",root=self.root)
 def test_job_creation_ids_uuid_and_resume_state(self):
  a=create_job("A",self.root);b=create_job("B",self.root);self.assertEqual((a["job_id"],b["job_id"]),("JOB_000001","JOB_000002"));self.assertNotEqual(a["uuid"],b["uuid"]);self.assertEqual(load_job(a["job_id"],self.root)["pipeline"]["research"],"PENDING")
 def test_state_machine(self):
  validate_transition("PENDING","RUNNING");validate_transition("RUNNING","COMPLETED")
  with self.assertRaises(InvalidTransition):validate_transition("COMPLETED","RUNNING")
  validate_transition("COMPLETED","RUNNING",force=True)
 def test_job_transition_persisted(self):
  job=create_job("A",self.root);transition(job,"research","RUNNING",self.root);self.assertEqual(load_job(job["job_id"],self.root)["attempts"]["research"],1)
 def test_retry_limit_blocks(self):
  from src.pipeline import _stage
  job=create_job("A",self.root);job["pipeline"]["research"]="FAILED";job["attempts"]["research"]=2
  with self.assertRaises(RuntimeError):_stage(job,"research",self.root,lambda:None)
  self.assertEqual(load_job(job["job_id"],self.root)["pipeline"]["research"],"BLOCKED")
 def test_atomic_write_no_temp_left(self):
  p=self.root/"x.json";atomic_write_json(p,{"x":1});self.assertEqual(load_json(p),{"x":1});self.assertEqual(list(self.root.glob("*.tmp")),[])
 def test_research_fact_script_schemas(self):
  job=create_job("Stars",self.root);research=MockResearchProvider().research(job);validate_research(research);self.assertEqual(validate_facts(research)["decision"],"PASS");script=generate_script(job,research,12,"educational","en");self.assertEqual(validate_script(script,research,2,100)["decision"],"PASS");self.assertTrue(plan_scenes(script)["scenes"])
 def test_metadata_schema(self):validate_metadata({"title":"A","description":"B","privacy_status":"private"})
 def test_config_redacts_credential_paths(self):
  safe=Settings(youtube_client_secrets="secret.json",youtube_token_file="token.json").safe_dict();self.assertEqual(safe["youtube_client_secrets"],"<configured>");self.assertNotIn("secret.json",str(safe))
 def test_final_checker_all_decisions_and_schema(self):
  good={"research":{},"facts":{"decision":"PASS"},"script_validation":{"decision":"PASS"},"technical":{"decision":"PASS"},"metadata_valid":True,"thumbnail_valid":True,"policy_valid":True};good["research"]={"ok":1};report=final_check(good);self.assertEqual(report["decision"],"PASS");self.assertTrue(validate_final_report(report))
  good["script_validation"]={"decision":"REGENERATE"};self.assertEqual(final_check(good)["decision"],"REGENERATE")
  good["script_validation"]={"decision":"BLOCK"};self.assertEqual(final_check(good)["decision"],"BLOCK")
 def test_final_checker_malformed_missing_low_confidence(self):
  self.assertFalse(validate_final_report(None));self.assertFalse(validate_final_report({"decision":"PASS"}));self.assertFalse(validate_final_report({"decision":"UNKNOWN","checks":{},"problems":[],"required_fixes":[],"affected_stages":[],"confidence":1}));self.assertFalse(validate_final_report({"decision":"PASS","checks":{"research":"PASS","facts":"PASS","script":"PASS","technical":"PASS","metadata":"PASS","thumbnail":"PASS","policy":"PASS"},"problems":[],"required_fixes":[],"affected_stages":[],"confidence":.2}))
 def test_locking(self):
  path=self.root/"lock"
  with JobLock(path):
   with self.assertRaises(LockBusy):JobLock(path).__enter__()
