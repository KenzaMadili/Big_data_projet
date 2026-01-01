# analyse_logs.py
# Compatible Python 2.7 et PySpark de Cloudera QuickStart VM

from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.functions import col, count, when

# Initialisation Spark
sc = SparkContext(appName="LogAnalysis")
sqlContext = SQLContext(sc)

# Chemin HDFS des logs
hdfs_path = "hdfs:///user/cloudera/logs/raw/date=2025-01-10/*/*.json"

# Lecture des logs
logs_df = sqlContext.read.json(hdfs_path)

# Affichage schema
print("Schema des logs :")
logs_df.printSchema()

# Feature engineering simple
# 1. Nombre de logs par IP
ip_count_df = logs_df.groupBy("ip").agg(count("*").alias("log_count"))

# 2. Nombre d'erreurs par IP (status != 200)
error_df = logs_df.groupBy("ip").agg(
    count(when(col("status") != 200, 1)).alias("error_count")
)

# 3. Détection simple d'anomalies
# On considère anomalie si status != 200 ou log_type == "anomaly"
anomaly_df = logs_df.filter((col("status") != 200) | (col("log_type") == "anomaly"))

# Sauvegarde des résultats en Parquet dans HDFS
ip_count_df.write.mode("overwrite").parquet(
    "hdfs:///user/cloudera/logs/processed/ip_count"
)
error_df.write.mode("overwrite").parquet(
    "hdfs:///user/cloudera/logs/processed/error_count"
)
anomaly_df.write.mode("overwrite").parquet(
    "hdfs:///user/cloudera/logs/processed/anomalies"
)

# Optionnel : sauvegarde Hive (si HiveServer2 actif)
try:
    sqlContext.sql("CREATE DATABASE IF NOT EXISTS log_analysis")
    ip_count_df.registerTempTable("ip_count_temp")
    sqlContext.sql("DROP TABLE IF EXISTS log_analysis.ip_count")
    sqlContext.sql("CREATE TABLE log_analysis.ip_count AS SELECT * FROM ip_count_temp")

    anomaly_df.registerTempTable("anomaly_temp")
    sqlContext.sql("DROP TABLE IF EXISTS log_analysis.anomalies")
    sqlContext.sql("CREATE TABLE log_analysis.anomalies AS SELECT * FROM anomaly_temp")
except Exception as e:
    print("Hive non disponible, skipping Hive save:", e)

print("Analyse des logs terminée avec succès !")
