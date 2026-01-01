#!/bin/bash
echo "🚀 DEMARRAGE DES SERVICES..."

# 1. API (Port 5000)
cd api
if [ ! -d "venv" ]; then
    virtualenv -p python3.4 venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi
nohup python app.py > ../logs/api.log 2>&1 &
echo "✅ API démarrée (Port 5000)"

# 2. Frontend (Port 8080)
cd ../frontend
nohup python3.4 -m http.server 8080 > ../logs/frontend.log 2>&1 &
echo "✅ Dashboard démarré (Port 8080)"

echo "🌍 Accès: http://localhost:8080/dashboard.html"