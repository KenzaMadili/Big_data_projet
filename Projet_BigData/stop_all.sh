#!/bin/bash
# stop_all.sh - Version Compatible Cloudera CentOS 6

echo "🛑 ARRÊT DU SYSTÈME..."
echo "======================"

# 1. Arrêter le Frontend (Dashboard)
echo "🖥️  Arrêt du Frontend..."
# On cherche le processus Python qui tourne sur le port 8080
PID_FRONT=$(netstat -tulpn 2>/dev/null | grep :8080 | awk '{print $7}' | cut -d/ -f1)

if [ -n "$PID_FRONT" ]; then
    kill $PID_FRONT
    echo "✅ Frontend arrêté (PID: $PID_FRONT)"
else
    # Sécurité supplémentaire avec pkill
    pkill -f "http.server" && echo "✅ Frontend arrêté (via pkill)" || echo "ℹ️  Frontend déjà arrêté"
fi

# 2. Arrêter l'API (Backend)
echo "🌐 Arrêt de l'API..."
# On cherche les processus Gunicorn
pkill -f gunicorn
if [ $? -eq 0 ]; then
    echo "✅ API arrêtée"
else
    echo "ℹ️  API déjà arrêtée"
fi

# 3. Arrêter Redis (Optionnel sur Cloudera)
# Sur Cloudera, Redis est souvent un service système qu'on préfère laisser tourner.
# Mais si tu veux vraiment l'arrêter :
# service redis stop
echo "ℹ️  Redis laissé actif (service système)"

echo ""
echo "✅ TOUT EST ARRÊTÉ."