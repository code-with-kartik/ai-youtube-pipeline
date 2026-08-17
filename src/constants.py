from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_ROOT = PROJECT_ROOT / "data"
STAGES = (
    "research", "fact_validation", "script", "script_validation", "scene_plan",
    "voice", "visuals", "subtitles", "render", "technical_qc", "metadata",
    "thumbnail", "final_checker", "upload", "archive", "cleanup", "analytics",
)
MANDATORY_FINAL_CHECKS = {"research", "facts", "script", "technical", "metadata", "thumbnail", "policy"}
STAGE_STATES = {"PENDING", "RUNNING", "COMPLETED", "FAILED", "BLOCKED", "REGENERATE", "SKIPPED"}

