import os
import sys
from datetime import datetime
from pyspark.sql import SparkSession

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.logger import logger


def get_processing_date():
    return os.getenv("PROCESSING_DATE", datetime.today().strftime("%Y-%m-%d"))


def verify_gold_layer(spark, path):
    logger.info(f"🔍 Verificando Gold em: {path}")

    if not os.path.exists(path):
        logger.error(f"❌ Diretório Gold não encontrado: {path}")
        return

    delta_log = os.path.join(path, "_delta_log")
    if not os.path.exists(delta_log):
        logger.error("❌ _delta_log ausente. Não é um diretório Delta válido.")
        return

    try:
        df = spark.read.format("delta").load(path)
        count = df.count()
        logger.info(f"✅ Gold carregada com sucesso. Registros: {count}")

        df.show(truncate=False)

    except Exception as e:
        logger.error(f"❌ Erro ao verificar Gold: {str(e)}")


if __name__ == "__main__":
    processing_date = get_processing_date()
    path = f"/home/project/data/gold/processing_date={processing_date}"

    spark = (
        SparkSession.builder
        .appName("Verify Gold")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.jars.packages", "io.delta:delta-core_2.12:2.3.0")
        .getOrCreate()
    )

    verify_gold_layer(spark, path)
