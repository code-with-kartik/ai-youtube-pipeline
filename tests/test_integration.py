import shutil,tempfile,unittest
from pathlib import Path
from src.config import Settings
from src.io_utils import load_json
from src.job_manager import create_job,load_job
from src.pipeline import publish_job,queue_for_upload,run_job
from src.storage.archive import archive_job

@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),"FFmpeg required")
class IntegrationTests(unittest.TestCase):
 def test_complete_local_pipeline_resume_dry_publish_archive(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);settings=Settings(storage_root=root,width=320,height=240,target_duration=10,min_duration=2,max_duration=120)
   job=create_job("How Black Holes Work",root);done=run_job(job["job_id"],settings);self.assertEqual(done["status"],"READY_TO_UPLOAD");video=root/"jobs"/job["job_id"]/"render"/"final.mp4";self.assertGreater(video.stat().st_size,1024);self.assertEqual(load_json(root/"jobs"/job["job_id"]/"reports"/"technical_qc.json")["decision"],"PASS");self.assertEqual(load_json(root/"jobs"/job["job_id"]/"reports"/"final_checker.json")["decision"],"PASS")
   attempts=dict(load_job(job["job_id"],root)["attempts"]);run_job(job["job_id"],settings);self.assertEqual(load_job(job["job_id"],root)["attempts"],attempts)
   run_job(job["job_id"],settings,"render");regenerated=load_job(job["job_id"],root)["attempts"]
   for stage in ("render","technical_qc","final_checker"):self.assertEqual(regenerated[stage],attempts[stage]+1)
   self.assertEqual(queue_for_upload(job["job_id"],settings)["status"],"QUEUED");self.assertEqual(publish_job(job["job_id"],settings)["status"],"DRY_RUN");self.assertIn("render/final.mp4",archive_job(root/"jobs"/job["job_id"])["files"])
