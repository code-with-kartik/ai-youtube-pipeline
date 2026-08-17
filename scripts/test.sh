#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m unittest discover -s tests -v

