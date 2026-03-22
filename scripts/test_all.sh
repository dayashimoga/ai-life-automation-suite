#!/bin/bash
set -e

echo "Testing all applications..."

./scripts/test_memory-journal-app.sh
./scripts/test_doomscroll-breaker-app.sh
./scripts/test_visual-intelligence-app.sh

echo "All tests passed successfully!"
