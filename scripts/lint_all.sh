#!/bin/bash
set -e

APPS=("memory-journal-app" "doomscroll-breaker-app" "visual-intelligence-app")

for APP in "${APPS[@]}"; do
    echo "Linting $APP..."
    cd "apps/$APP"
    python -m venv .venv_tmp
    source .venv_tmp/Scripts/activate || source .venv_tmp/bin/activate
    pip install ruff black
    ruff check .
    black --check .
    deactivate
    rm -rf .venv_tmp
    cd ../..
done

echo "All linting passed successfully!"
