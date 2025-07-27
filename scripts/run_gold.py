import sys
import os
from datetime import datetime
import pytz
from pyspark.sql import SparkSession

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.transform import run_gold_transformation
from src.logger import logger


def get_env_variable(name: str, default=None):
    return os.getenv(name, default)


def get_processing_date() -> str:
    timezone = pytz.timezone("America/Sao_Paulo")
    today = datetime.now(timezone).date()
    return today.strftime("%Y-%m-%d")


if __name__ == "__main__":
    processing_date = get_env_variable("PROCESSING_DATE") or get_processing_date()

    logger.info(f"🚀 Executando Gold para {processing_date}...")

    spark = (
        SparkSession.builder
        .appName("Gold Layer Runner")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.sql.debug.maxToStringFields", 2000)
        .config("spark.jars.packages", "io.delta:delta-core_2.12:2.3.0")
        .getOrCreate()
    )

    run_gold_transformation(spark, processing_date)
