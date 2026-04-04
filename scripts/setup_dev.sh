#!/usr/bin/env bash
set -euo pipefail

if [ -z "${VIRTUAL_ENV:-}" ] && [ -z "${CONDA_PREFIX:-}" ]; then
  echo "Activate a virtualenv or conda env before running this script."
  exit 1
fi

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python -m pre_commit install

echo "Python development environment ready."

echo "Run 'cd frontend && npm ci' separately if you need frontend dependencies."
