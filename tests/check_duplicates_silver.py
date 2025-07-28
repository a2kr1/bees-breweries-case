from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count
from pathlib import Path
import os
import sys

from src.logger import setup_logger

logger = setup_logger()

def main():
    # ✅ Recupera data de processamento
    processing_date = os.getenv("PROCESSING_DATE")
    if not processing_date:
        logger.error("❌ Variável de ambiente PROCESSING_DATE não definida.")
        sys.exit(1)

    logger.info(f"📅 Checando duplicatas na Silver para PROCESSING_DATE = {processing_date}")

    # ✅ Inicializa Spark com suporte a Delta Lake
    try:
        spark = (
            SparkSession.builder.appName("CheckDuplicatesSilver")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            .getOrCreate()
        )
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar SparkSession com Delta: {e}", exc_info=True)
        sys.exit(1)

    # ✅ Caminho da silver
    silver_path = Path("/home/project/data/silver")

    try:
        df_filtered = df.filter(col("processing_date") == processing_date)
        # Leitura já estava correta, mas o load precisa considerar subpastas:
        df = spark.read.format("delta").load(str(silver_path))

        df_duplicates = (
            df_filtered.groupBy("id", "processing_date")
            .agg(count("*").alias("count"))
            .filter(col("count") > 1)
        )

        count_dupes = df_duplicates.count()

        if count_dupes > 0:
            logger.warning(f"⚠️ Encontrados {count_dupes} registros duplicados para a data {processing_date}")
            df_duplicates.show(truncate=False)
        else:
            logger.info("✅ Nenhuma duplicata encontrada para o conjunto verificado.")

    except Exception as e:
        logger.error(f"❌ Erro durante a checagem de duplicatas: {e}", exc_info=True)
        sys.exit(1)
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
