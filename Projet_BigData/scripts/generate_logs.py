# -*- coding: utf-8 -*-
import json
import random
import time
import os
from datetime import datetime

# Configuration
sources = ["nginx", "apache", "app", "security"]
ips_normal = ["192.168.1.%d" % i for i in range(1, 50)]
urls = ["/", "/login", "/dashboard", "/api/data", "/logout"]
methods = ["GET", "POST"]

# Création des dossiers locaux si inexistants
os.system("mkdir -p ../data/raw/date=2025-01-10/normal")
os.system("mkdir -p ../data/raw/date=2025-01-10/anomaly")

def generate_normal_log():
    return {
        "timestamp": datetime.now().isoformat(),
        "ip": random.choice(ips_normal),
        "method": random.choice(methods),
        "url": random.choice(urls),
        "status": 200,
        "response_time": random.randint(50, 300),
        "label": 0
    }

def generate_anomaly_log():
    # Simulation d'attaques ou pannes
    case = random.choice(["slow", "error", "flood"])
    log = {
        "timestamp": datetime.now().isoformat(),
        "ip": "10.10.10.10", # IP Attaquant
        "method": "POST",
        "url": "/login",
        "label": 1
    }
    
    if case == "slow":
        log["status"] = 200
        log["response_time"] = random.randint(3000, 10000) # Très lent
    elif case == "error":
        log["status"] = random.choice([404, 500, 503])
        log["response_time"] = random.randint(50, 100)
    else: # flood
        log["status"] = 200
        log["response_time"] = random.randint(50, 100)
        
    return log

# Noms de fichiers dynamiques (Timestamp)
ts = str(int(time.time()))
file_normal = "../data/raw/date=2025-01-10/normal/logs_norm_" + ts + ".json"
file_anomaly = "../data/raw/date=2025-01-10/anomaly/logs_anom_" + ts + ".json"

print ">>> Generation: " + file_normal
with open(file_normal, "w") as f:
    for i in range(2000): # 2000 logs normaux
        f.write(json.dumps(generate_normal_log()) + "\n")

print ">>> Generation: " + file_anomaly
with open(file_anomaly, "w") as f:
    for i in range(100): # 100 anomalies
        f.write(json.dumps(generate_anomaly_log()) + "\n")
