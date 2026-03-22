#!/bin/bash
set -e

APP_DIR="apps/memory-journal-app"
echo "Starting test script for memory-journal-app..."

cd $APP_DIR

echo "1. Creating temporary virtual environment..."
python -m venv .venv_tmp

echo "2. Activating environment..."
source .venv_tmp/Scripts/activate || source .venv_tmp/bin/activate

echo "3. Installing dependencies..."
pip install -r requirements.txt
pip install pytest pytest-cov ruff black httpx

echo "4. Running linters and formatting checks..."
ruff check .
black --check .

echo "5. Running tests with coverage..."
pytest --cov=. --cov-fail-under=90

echo "6. Deactivating environment..."
deactivate

echo "7. Deleting virtual environment..."
rm -rf .venv_tmp

echo "Memory Journal App checks passed successfully!"
