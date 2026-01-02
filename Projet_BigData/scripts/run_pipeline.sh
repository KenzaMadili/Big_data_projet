#!/bin/bash
# ============================================================
# PIPELINE AUTOMATISÉ - VERSION FINALE (AVEC NETTOYAGE)
# ============================================================

echo "=========================================="
echo ">>> ETAPE 0 : NETTOYAGE PREALABLE (RESET)"
echo "=========================================="
# 1. Nettoyage Local (Supprime les anciens json générés)
rm -rf ../data/raw/date=2025-01-10/*
echo "✅ Logs locaux supprimés"

# 2. Nettoyage HDFS (Supprime les dossiers de la veille pour éviter les doublons)
# 2>/dev/null cache les erreurs si le dossier n'existe pas encore
hdfs dfs -rm -r -skipTrash /logs/raw/date=2025-01-10 2>/dev/null
hdfs dfs -rm -r -skipTrash /logs/processed/date=2025-01-10 2>/dev/null
hdfs dfs -rm -r -skipTrash /logs/results/date=2025-01-10 2>/dev/null
echo "✅ HDFS nettoyé"

# 3. Nettoyage Impala
impala-shell -B --quiet -q "DROP TABLE IF EXISTS detected_anomalies;" 2>/dev/null
echo "✅ Table Impala nettoyée"

echo "=========================================="
echo ">>> ETAPE 1 : GENERATION DE LOGS"
echo "=========================================="
python generate_logs.py

echo "=========================================="
echo ">>> ETAPE 2 : PREPARATION HDFS"
echo "=========================================="
# On recrée les dossiers propres
hdfs dfs -mkdir -p /logs/raw/date=2025-01-10/
hdfs dfs -mkdir -p /logs/processed/date=2025-01-10/
hdfs dfs -mkdir -p /logs/results/date=2025-01-10/

echo "=========================================="
echo ">>> ETAPE 3 : UPLOAD VERS HDFS"
echo "=========================================="
hdfs dfs -put -f ../data/raw/date=2025-01-10/*/*.json /logs/raw/date=2025-01-10/

# Vérification
COUNT=$(hdfs dfs -ls /logs/raw/date=2025-01-10/ | grep .json | wc -l)
echo "[INFO] $COUNT fichiers trouves dans HDFS."

echo "=========================================="
echo ">>> ETAPE 4 : PRE-TRAITEMENT (Spark)"
echo "=========================================="
spark-submit preprocess_logs.py

echo "=========================================="
echo ">>> ETAPE 5 : DETECTION D'ANOMALIES (Spark ML)"
echo "=========================================="
spark-submit train_model.py

echo "=========================================="
echo ">>> ETAPE 5.5 : FIX PERMISSIONS (CRITIQUE)"
echo "=========================================="
# Indispensable pour qu'Impala puisse lire les fichiers écrits par root
hdfs dfs -chmod -R 777 /logs/results

echo "=========================================="
echo ">>> ETAPE 6 : RESULTATS (IMPALA)"
echo "=========================================="

# 1. Trouver le fichier modele automatiquement
PARQUET_FILE=$(hdfs dfs -ls /logs/results/date=2025-01-10/ | grep "part-r-00000" | head -n 1 | awk '{print $8}')

if [ -z "$PARQUET_FILE" ]; then
    echo "❌ ERREUR: Fichier Parquet non trouvé. Relancez train_model.py"
    exit 1
fi

echo "Fichier modele trouvé : $PARQUET_FILE"

# 2. Reconstruire la table proprement avec la structure exacte
impala-shell -q "
DROP TABLE IF EXISTS detected_anomalies;
CREATE EXTERNAL TABLE detected_anomalies 
LIKE PARQUET '$PARQUET_FILE'
STORED AS PARQUET
LOCATION '/logs/results/date=2025-01-10/';
INVALIDATE METADATA detected_anomalies;
REFRESH detected_anomalies;
"

echo ">>> TERMINE. Données prêtes pour le Dashboard."