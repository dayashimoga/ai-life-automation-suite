#!/bin/bash

echo "Cleaning up all temporary virtual environments..."

APPS=("memory-journal-app" "doomscroll-breaker-app" "visual-intelligence-app")
for APP in "${APPS[@]}"; do
    if [ -d "apps/$APP/.venv_tmp" ]; then
        echo "Removing apps/$APP/.venv_tmp"
        rm -rf "apps/$APP/.venv_tmp"
    fi
done

echo "Clean up done!"
