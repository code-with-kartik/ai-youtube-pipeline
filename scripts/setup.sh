#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
mkdir -p data/topics data/jobs logs
test -f data/topics/queue.json || printf '[]\n' > data/topics/queue.json
.venv/bin/python -m src.cli doctor
./scripts/test.sh

