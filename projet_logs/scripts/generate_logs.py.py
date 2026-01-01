import json
import random
from datetime import datetime

sources = ["nginx", "apache", "app", "security"]
ips_normal = ["192.168.1.%d" % i for i in range(1, 50)]
urls = ["/", "/login", "/dashboard", "/api/data", "/logout"]
methods = ["GET", "POST"]

def generate_normal_log():
    return {
        "timestamp": datetime.now().isoformat(),
        "source": random.choice(sources),
        "ip": random.choice(ips_normal),
        "method": random.choice(methods),
        "url": random.choice(urls),
        "status": 200,
        "response_time": random.randint(50, 300),
        "message": "OK",
        "log_type": "normal",
        "label": 0
    }

def generate_anomaly_log():
    return {
        "timestamp": datetime.now().isoformat(),
        "source": "security",
        "ip": "10.10.10.10",
        "method": "POST",
        "url": "/login",
        "status": random.choice([401, 403, 500]),
        "response_time": random.randint(1000, 5000),
        "message": "Suspicious activity",
        "log_type": "anomaly",
        "label": 1
    }

# Generate normal logs
f_normal = open("../data/raw/date=2025-01-10/normal/logs_normal.json", "w")
for i in range(10000):
    f_normal.write(json.dumps(generate_normal_log()) + "\n")
f_normal.close()

# Generate anomaly logs
f_anomaly = open("../data/raw/date=2025-01-10/anomaly/logs_anomaly.json", "w")
for i in range(1000):
    f_anomaly.write(json.dumps(generate_anomaly_log()) + "\n")
f_anomaly.close()

print("Logs generated successfully")