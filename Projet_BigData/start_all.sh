#!/bin/bash
# start_all.sh - Compatible Cloudera CentOS 6

# Robust relative path to find the script's directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "🚀 STARTING SERVICES..."

# 1. Start Redis (System V Init style)
service redis start >/dev/null 2>&1 || service redis-server start >/dev/null 2>&1
echo "✅ Redis active"

# 2. Start API (Backend)
cd api
# Activate the virtual environment we just created
source venv/bin/activate

# Kill old process if running
pkill -f gunicorn || true

# Start Gunicorn in background
# Using standard log files
nohup gunicorn --bind 0.0.0.0:5000 --workers 2 app:app > ../logs/api.log 2>&1 &
echo "✅ API started (Port 5000)"

# 3. Start Frontend (Dashboard)
cd ../frontend
# Kill old process if running
pkill -f http.server || true

# Explicitly use python3.4 for the web server
nohup python3.4 -m http.server 8080 > ../logs/frontend.log 2>&1 &
echo "✅ Dashboard started (Port 8080)"

echo ""
echo "=================================================="
echo "🌍 Access Dashboard here: http://localhost:8080/dashboard.html"
echo "=================================================="