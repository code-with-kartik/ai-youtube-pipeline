from __future__ import annotations
import json, os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from src.constants import DEFAULT_DATA_ROOT, PROJECT_ROOT

@dataclass(frozen=True)
class Settings:
    storage_root: Path = DEFAULT_DATA_ROOT
    publish_mode: str = "dry-run"
    ai_provider: str = "mock"
    voice_provider: str = "mock"
    visual_provider: str = "mock"
    thumbnail_provider: str = "mock"
    width: int = 1280
    height: int = 720
    frame_rate: int = 24
    min_duration: float = 2.0
    max_duration: float = 1800.0
    target_duration: float = 12.0
    language: str = "en"
    style: str = "educational"
    retry_limit: int = 2
    timeout_seconds: int = 120
    retention_days: int = 6
    burn_subtitles: bool = True
    require_subtitles: bool = True
    privacy_status: str = "private"
    youtube_client_secrets: str = ""
    youtube_token_file: str = ""
    def validate(self) -> None:
        if self.publish_mode not in {"dry-run", "production"}: raise ValueError("publish_mode must be dry-run or production")
        if self.width < 320 or self.height < 240 or self.frame_rate < 1: raise ValueError("invalid video dimensions/frame rate")
        if not 0 < self.min_duration <= self.target_duration <= self.max_duration: raise ValueError("invalid duration bounds")
        if not 0 <= self.retention_days <= 3650: raise ValueError("invalid retention_days")
        if not 0 <= self.retry_limit <= 10: raise ValueError("invalid retry_limit")
        if self.privacy_status not in {"private", "unlisted", "public"}: raise ValueError("invalid privacy_status")
    def safe_dict(self) -> dict[str, Any]:
        data = asdict(self); data["storage_root"] = str(self.storage_root)
        for key in ("youtube_client_secrets", "youtube_token_file"): data[key] = "<configured>" if data[key] else ""
        return data

def _read_dotenv(path: Path) -> None:
    if not path.exists(): return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        key, value = line.split("=", 1); os.environ.setdefault(key.strip(), value.strip().strip("'\""))

def load_settings(config_path: Path | None = None) -> Settings:
    _read_dotenv(PROJECT_ROOT / ".env")
    path = config_path or PROJECT_ROOT / "config" / "config.json"; data: dict[str, Any] = {}
    if path.exists(): data = json.loads(path.read_text(encoding="utf-8"))
    mapping = {"storage_root":"AIYT_STORAGE_ROOT","publish_mode":"AIYT_PUBLISH_MODE","ai_provider":"AIYT_AI_PROVIDER","voice_provider":"AIYT_VOICE_PROVIDER","visual_provider":"AIYT_VISUAL_PROVIDER","thumbnail_provider":"AIYT_THUMBNAIL_PROVIDER","youtube_client_secrets":"YOUTUBE_CLIENT_SECRETS","youtube_token_file":"YOUTUBE_TOKEN_FILE"}
    for field, env in mapping.items():
        if env in os.environ: data[field] = os.environ[env]
    if "storage_root" in data: data["storage_root"] = Path(data["storage_root"]).expanduser().resolve()
    settings = Settings(**data); settings.validate(); return settings

