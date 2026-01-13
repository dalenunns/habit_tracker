#!/bin/bash
set -e

echo "Starting Habit Tracker on 0.0.0.0:5000..."
# We use -u to ensure python logs appear in the HA Add-on logs immediately
python3 -u app.py