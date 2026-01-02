# -*- coding: utf-8 -*-
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.functions import col, unix_timestamp, hour, when

def main():
    sc = SparkContext(appName="Preprocessing_KMeans_Ready")
    sqlContext = SQLContext(sc)
    sc.setLogLevel("WARN")

    # Lecture des fichiers bruts
    input_path = "hdfs:///logs/raw/date=2025-01-10/*.json"
    output_path = "hdfs:///logs/processed/date=2025-01-10/"

    try:
        df_raw = sqlContext.read.json(input_path)
    except Exception as e:
        print "!!! Erreur lecture : " + str(e)
        return

    # 1. Nettoyage et Typage
    df_clean = df_raw \
        .withColumn("ts", unix_timestamp(col("timestamp"), "yyyy-MM-dd'T'HH:mm:ss")) \
        .withColumn("event_time", col("ts").cast("timestamp")) \
        .withColumn("response_time", col("response_time").cast("double")) \
        .withColumn("status", col("status").cast("integer")) \
        .filter(col("event_time").isNotNull())

    # 2. Feature Engineering (Creation de colonnes pour le ML)
    df_features = df_clean \
        .withColumn("hour", hour("event_time")) \
        .withColumn("is_error", when(col("status") >= 400, 1.0).otherwise(0.0)) \
        .withColumn("method_idx", when(col("method") == "GET", 0.0)
                                 .when(col("method") == "POST", 1.0)
                                 .otherwise(2.0))

    # Selection des colonnes finales
    final_df = df_features.select(
        "ip", "event_time", "label",
        "response_time", "hour", "is_error", "method_idx", "status"
    )

    final_df.write.mode("overwrite").parquet(output_path)
    print ">>> Preprocessing termine avec SUCCES."

if __name__ == "__main__":
    main()