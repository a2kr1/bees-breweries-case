import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import count
from datetime import datetime
import pytz

def get_processing_date():
    env_date = os.getenv("PROCESSING_DATE")
    if env_date:
        return env_date
    tz = pytz.timezone("America/Sao_Paulo")
    return datetime.now(tz).strftime("%Y-%m-%d")

def create_spark_session():
    return SparkSession.builder         .appName("CheckDuplicatesGold")         .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")         .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")         .getOrCreate()

def main():
    spark = create_spark_session()
    processing_date = get_processing_date()
    print(f"[INFO] 📅 PROCESSING_DATE: {processing_date}")

    df = spark.read.format("delta").load(f"/home/project/data/gold/{processing_date}")
    df.cache()

    print("[INFO] 🔍 Verificando duplicatas por ('state', 'brewery_type')")
    df.groupBy("state", "brewery_type").agg(count("*").alias("count")).filter("count > 1").show(10, truncate=False)

    df.unpersist()
    spark.stop()

if __name__ == "__main__":
    main()