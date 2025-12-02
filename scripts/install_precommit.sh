#!/usr/bin/env bash
set -euo pipefail

if [ -z "${VIRTUAL_ENV:-}" ]; then
  echo "Ative o venv antes de rodar este script."
  exit 1
fi

python -m pip install --upgrade pip
python -m pip install pre-commit ruff
pre-commit install --config scripts/pre-commit-config.yaml
pre-commit run --config scripts/pre-commit-config.yaml --all-files || true
