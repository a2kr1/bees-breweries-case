from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import os
import sys
from src.logger import setup_logger

logger = setup_logger()
spark = SparkSession.builder \
    .appName("Check Duplicates - Silver") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

processing_date = os.getenv("PROCESSING_DATE")
if not processing_date:
    logger.error("PROCESSING_DATE não foi definido.")
    sys.exit(1)

logger.info(f"📅 PROCESSING_DATE: {processing_date}")

try:
    df = spark.read.format("delta") \
        .load("/home/project/data/silver") \
        .where(f"processing_date = '{processing_date}'")

    duplicate_count = df.groupBy("id").count().filter(col("count") > 1).count()

    if duplicate_count > 0:
        logger.warning(f"⚠️ Encontrados {duplicate_count} registros duplicados na camada Silver!")
    else:
        logger.info("✅ Nenhum registro duplicado encontrado na camada Silver.")

except Exception as e:
    logger.error(f"Erro ao verificar duplicatas na Silver: {e}")
    sys.exit(1)
finally:
    spark.stop()
