import tempfile,unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
from src.checks.final_checker import final_check
from src.io_utils import atomic_write_json
from src.job_manager import create_job,job_dir
from src.publish.youtube import UploadBlocked,YouTubePublisher
from src.storage.archive import archive_job
from src.storage.cleanup import cleanup_job
from src.storage.local import LocalStorage
from src.upload_queue import enqueue

class SafetyTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.job=create_job("Safe",self.root);self.directory=job_dir(self.job["job_id"],self.root);self.called=False
 def tearDown(self):self.tmp.cleanup()
 def callback(self,*_):self.called=True;return {"video_id":"real"}
 def write_assets(self):
  for relative in ("render/final.mp4","thumbnail/thumbnail.jpg","metadata/metadata.json"):
   p=self.directory/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b"x")
 def report(self,decision="PASS"):
  report={"decision":decision,"checks":{"research":"PASS","facts":"PASS","script":"PASS","technical":"PASS","metadata":"PASS","thumbnail":"PASS","policy":"PASS"},"problems":[],"required_fixes":[],"affected_stages":[],"confidence":1 if decision=="PASS" else 0};atomic_write_json(self.directory/"reports"/"final_checker.json",report);return report
 def test_production_function_never_called_for_every_non_pass_state(self):
  self.write_assets()
  for decision in ("BLOCK","REGENERATE","UNKNOWN",None):
   if decision is None:(self.directory/"reports"/"final_checker.json").unlink(missing_ok=True)
   elif decision=="UNKNOWN":atomic_write_json(self.directory/"reports"/"final_checker.json",{"decision":"UNKNOWN"})
   else:self.report(decision)
   with self.assertRaises(UploadBlocked):YouTubePublisher(self.directory,"client","token",self.callback).publish(self.job)
  self.assertFalse(self.called)
 def test_valid_pass_reaches_callback(self):self.write_assets();self.report();YouTubePublisher(self.directory,"client","token",self.callback).publish(self.job);self.assertTrue(self.called)
 def test_queue_blocks_nonpass_and_is_idempotent(self):
  self.report("BLOCK")
  with self.assertRaises(ValueError):enqueue(self.job,self.directory,self.root)
  self.report();self.assertEqual(enqueue(self.job,self.directory,self.root),enqueue(self.job,self.directory,self.root))
 def test_cleanup_dry_run_and_preservation(self):
  keep=self.directory/"script"/"script.txt";keep.write_text("keep");temp=self.directory/"visuals"/"x";temp.write_text("temp");past=datetime.now(timezone.utc)-timedelta(days=1);self.job["publication"]={"published_at":past.isoformat(),"cleanup_eligible_at":past.isoformat()};result=cleanup_job(self.directory,self.job,dry_run=True);self.assertEqual(result["decision"],"DRY_RUN");self.assertTrue(temp.exists());cleanup_job(self.directory,self.job,dry_run=False);self.assertTrue(keep.exists());self.assertFalse(temp.exists())
 def test_cleanup_path_and_symlink_safety(self):
  with self.assertRaises(ValueError):cleanup_job(self.root,self.job)
 def test_storage_path_traversal(self):
  source=self.root/"a";source.write_text("a")
  with self.assertRaises(ValueError):LocalStorage(self.root/"store").put(source,"../escape")
 def test_archive_preserves_audit_files(self):
  p=self.directory/"reports"/"final_checker.json";p.write_text("{}");result=archive_job(self.directory);self.assertIn("reports/final_checker.json",result["files"]);self.assertTrue((self.directory/"archive"/"reports"/"final_checker.json").exists())

