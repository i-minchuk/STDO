#!/usr/bin/env bash
set -euo pipefail

if [ -z "${VIRTUAL_ENV:-}" ] && [ -z "${CONDA_PREFIX:-}" ]; then
  echo "Activate a Python environment before running this script."
  exit 1
fi

nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > /tmp/uvicorn.log 2>&1 &

cd frontend
nohup npm run dev -- --host 0.0.0.0 > /tmp/vite.log 2>&1 &

echo "Backend and frontend development servers started."
