import sys
import os
from datetime import datetime, timedelta
import pytz
from pyspark.sql import SparkSession

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.transform import run_silver_transformation
from src.logger import logger  # Importa diretamente o logger já configurado


def get_env_variable(name: str, default=None):
    return os.getenv(name, default)


def get_processing_date(delta_days: int = 0) -> str:
    timezone = pytz.timezone("America/Sao_Paulo")
    today = datetime.now(timezone).date()
    processing_date = today + timedelta(days=delta_days)
    return processing_date.strftime("%Y-%m-%d")


if __name__ == "__main__":
    try:
        delta_days = int(get_env_variable("DELTA_DAYS", 0))
    except ValueError:
        logger.warning("⚠️ DELTA_DAYS inválido. Usando 0.")
        delta_days = 0

    processing_date = get_env_variable("PROCESSING_DATE")
    if not processing_date:
        processing_date = get_processing_date(delta_days)

    logger.info(f"🔄 DELTA_DAYS configurado: {delta_days}")
    logger.info(f"🚀 Processando {processing_date}...")

    spark = (
        SparkSession.builder
        .appName("Silver Layer Runner")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.sql.debug.maxToStringFields", 2000)
        .config("spark.jars.packages", "io.delta:delta-core_2.12:2.3.0")
        .getOrCreate()
    )

    run_silver_transformation(spark, processing_date, delta_days)
