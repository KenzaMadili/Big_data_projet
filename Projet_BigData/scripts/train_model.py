# -*- coding: utf-8 -*-
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.functions import col, when, lit
import math

def main():
    sc = SparkContext(appName="AnomalyDetection_Manual_Dist")
    sqlContext = SQLContext(sc)
    sc.setLogLevel("WARN")

    input_path = "hdfs:///logs/processed/date=2025-01-10/"
    output_path = "hdfs:///logs/results/date=2025-01-10/"

    # 1. Chargement
    try:
        df = sqlContext.read.parquet(input_path)
    except Exception as e:
        print "!!! Erreur lecture : " + str(e)
        return

    # 2. Entrainement : Calcul du "Centre de Normalité" (Centroid)
    print ">>> Calcul du profil de reference (Centroid)..."
    stats = df.select(
        col("response_time"), col("hour"), col("is_error"), col("method_idx")
    ).agg({
        "response_time": "avg", "hour": "avg", "is_error": "avg", "method_idx": "avg"
    }).collect()[0]

    avg_resp = stats["avg(response_time)"] or 0.0
    avg_hour = stats["avg(hour)"] or 0.0
    avg_err  = stats["avg(is_error)"] or 0.0
    avg_meth = stats["avg(method_idx)"] or 0.0

    print ">>> Centre du Cluster Normal : Resp=" + str(avg_resp)

    # 3. Detection : Distance Euclidienne
    bc_resp = sc.broadcast(avg_resp)
    bc_hour = sc.broadcast(avg_hour)
    bc_err  = sc.broadcast(avg_err)
    bc_meth = sc.broadcast(avg_meth)

    def get_distance(r_time, r_hour, r_err, r_meth):
        d1 = (float(r_time) - bc_resp.value) / 5000.0
        d2 = (float(r_hour) - bc_hour.value) / 24.0
        d3 = (float(r_err)  - bc_err.value)  * 5.0 
        d4 = (float(r_meth) - bc_meth.value) / 2.0
        return math.sqrt(d1*d1 + d2*d2 + d3*d3 + d4*d4)

    results_rdd = df.rdd.map(lambda row: (
        row.ip, row.event_time, row.status, row.response_time, row.label,
        float(get_distance(row.response_time, row.hour, row.is_error, row.method_idx))
    ))

    schema = ["ip", "event_time", "status", "response_time", "label", "anomaly_score"]
    df_results = sqlContext.createDataFrame(results_rdd, schema)

    # 4. Application du Seuil (Threshold = 2.0)
    THRESHOLD = 2.0
    
    df_final = df_results.withColumn("prediction", 
        when(col("anomaly_score") > THRESHOLD, 1).otherwise(0)
    ).withColumn("cluster", lit(0))

    # 5. Sauvegarde
    anomalies = df_final.filter("prediction = 1").count()
    print ">>> Anomalies detectees : " + str(anomalies)

    df_final.write.mode("overwrite").parquet(output_path)
    print ">>> Sauvegarde terminee."

if __name__ == "__main__":
    main()