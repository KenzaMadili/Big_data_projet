# -*- coding: utf-8 -*-
from flask import Flask, jsonify
import subprocess
import logging
from logging.handlers import RotatingFileHandler
import os
import re

app = Flask(__name__)

# LOGGING
if not os.path.exists('../logs'):
    os.makedirs('../logs')
handler = RotatingFileHandler('../logs/api.log', maxBytes=1000000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# --- CORRECTION CORS (AUTORISER LE DASHBOARD) ---
@app.after_request
def after_request(response):
    # On autorise tout le monde (*) a lire les donnees
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
# ------------------------------------------------

def run_impala_query(query):
    full_query = "USE default; " + query
    cmd = ['impala-shell', '-B', '--quiet', '--output_delimiter=,', '-q', full_query]
    
    # ISOLATION IMPALA (Python 2 vs 3)
    env = os.environ.copy()
    if 'VIRTUAL_ENV' in env:
        venv_bin = os.path.join(env['VIRTUAL_ENV'], 'bin')
        env['PATH'] = env['PATH'].replace(venv_bin + ':', '').replace(':' + venv_bin, '').replace(venv_bin, '')
    
    try:
        app.logger.info("CMD: " + str(cmd))
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        out, err = p.communicate()
        
        if out:
            raw = out.decode('utf-8', errors='ignore').strip()
            return raw
        return None
    except Exception as e:
        app.logger.error("EXEC ERROR: " + str(e))
        return None

@app.route('/')
def index():
    return "API Online"

@app.route('/api/stats')
def stats():
    raw = run_impala_query("SELECT count(*) FROM detected_anomalies WHERE prediction=1")
    total = 0
    if raw:
        clean_text = re.sub(r'[^\d]', ' ', raw)
        numbers = [int(n) for n in clean_text.split() if n.isdigit()]
        if numbers:
            total = max(numbers)
    return jsonify({"total_anomalies": total, "status": "success"})

@app.route('/api/anomalies')
def anomalies():
    query = "SELECT ip, cast(event_time as string), anomaly_score, response_time, status FROM detected_anomalies WHERE prediction=1 ORDER BY anomaly_score DESC LIMIT 10"
    raw = run_impala_query(query)
    data = []
    if raw:
        for line in raw.split('\n'):
            if "Fetched" in line or "Connected" in line: continue
            parts = line.split(',')
            if len(parts) >= 4:
                try:
                    data.append({
                        "ip": parts[0].strip(),
                        "time": parts[1].strip(),
                        "score": float(parts[2]),
                        "resp_time": float(parts[3]),
                        "status": int(parts[4]) if len(parts)>4 else 0
                    })
                except: continue
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)