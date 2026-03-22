#!/bin/bash
set -e

echo "========================================="
echo -e "\e[36m AI Life Automation Suite - Test Runner\e[0m"
echo "========================================="

APPS=(
    "unified-dashboard-app"
    "memory-journal-app"
    "doomscroll-breaker-app"
    "visual-intelligence-app"
    "micro-habit-engine"
)
FAILED=0

for app in "${APPS[@]}"; do
    echo -e "\n\e[33m➤ Running Tests for $app ...\e[0m"

    pushd "apps/$app" > /dev/null
    if [ -f ".venv_tmp/Scripts/python.exe" ]; then
        PY_CMD=".venv_tmp/Scripts/python.exe"
    elif [ -f ".venv_tmp/bin/python" ]; then
        PY_CMD=".venv_tmp/bin/python"
    else
        PY_CMD="python"
    fi
    if $PY_CMD -m pytest tests/ -v --tb=short; then
        echo -e "\e[32m✅ $app tests PASSED!\e[0m"
    else
        echo -e "\e[31m❌ $app tests FAILED!\e[0m"
        FAILED=1
    fi
    popd > /dev/null
done

echo -e "\n========================================="
if [ $FAILED -ne 0 ]; then
    echo -e "\e[31m⚠️  SOME TESTS FAILED.\e[0m"
    exit 1
else
    echo -e "\e[32m🚀 ALL TESTS PASSED!\e[0m"
    exit 0
fi
