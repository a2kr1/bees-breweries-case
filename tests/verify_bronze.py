import os
from pyspark.sql import SparkSession
from src.logger import setup_logger

logger = setup_logger()

PROCESSING_DATE = os.getenv("PROCESSING_DATE")

if not PROCESSING_DATE:
    raise ValueError("PROCESSING_DATE não foi definido.")

BRONZE_PATH = f"/home/project/data/bronze/{PROCESSING_DATE}"

logger.info(f"🔍 Verificando Bronze em: {BRONZE_PATH}")

spark = (
    SparkSession.builder.appName("Verify Bronze")
    .config("spark.jars.packages", "io.delta:delta-core_2.12:2.3.0")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .getOrCreate()
)

try:
    df = spark.read.format("delta").load(BRONZE_PATH)
    logger.info(f"✅ Bronze carregada com sucesso. Registros: {df.count()}")
    df.show(5)
except Exception as e:
    logger.error(f"❌ Falha ao carregar Bronze: {e}")
