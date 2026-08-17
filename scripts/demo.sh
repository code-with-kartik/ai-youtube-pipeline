#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
demo_root="$(mktemp -d /tmp/aiyt-demo.XXXXXX)"
trap 'rm -rf -- "$demo_root"' EXIT
AIYT_STORAGE_ROOT="$demo_root" AIYT_PUBLISH_MODE=dry-run .venv/bin/python -m src.cli add-topic "How Black Holes Work"
AIYT_STORAGE_ROOT="$demo_root" AIYT_PUBLISH_MODE=dry-run .venv/bin/python -m src.cli run-next
AIYT_STORAGE_ROOT="$demo_root" AIYT_PUBLISH_MODE=dry-run .venv/bin/python -m src.cli queue-upload JOB_000001
AIYT_STORAGE_ROOT="$demo_root" AIYT_PUBLISH_MODE=dry-run .venv/bin/python -m src.cli publish JOB_000001
AIYT_STORAGE_ROOT="$demo_root" .venv/bin/python -m src.cli archive JOB_000001
test -s "$demo_root/jobs/JOB_000001/render/final.mp4"
echo "DEMO PASS: local pipeline rendered, gated, dry-run published, and archived"

