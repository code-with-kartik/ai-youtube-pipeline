#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
.venv/bin/python -m src.cli doctor
.venv/bin/python -m src.cli resume
.venv/bin/python -m src.cli run-next

