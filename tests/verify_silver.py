import os
from pyspark.sql import SparkSession
from src.logger import setup_logger
from datetime import datetime

logger = setup_logger()

def main():
    processing_date = os.getenv("PROCESSING_DATE")
    if not processing_date:
        processing_date = datetime.now().strftime("%Y-%m-%d")
        logger.info(f"PROCESSING_DATE não definido. Usando data atual: {processing_date}")

    logger.info(f"Verificando Silver para PROCESSING_DATE = {processing_date}")

    spark = SparkSession.builder \
        .appName("Verify Silver") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

    try:
        df = spark.read.format("delta").load("/home/project/data/silver").where(f"processing_date = '{processing_date}'")
        logger.info("Leitura do Delta Lake na camada Silver realizada com sucesso.")
        df.printSchema()
        df.show(5, truncate=False)

        expected_columns = [
            "id", "name", "state", "brewery_type", "processing_date", "silver_load_date"
        ]
        missing_cols = [col for col in expected_columns if col not in df.columns]
        if missing_cols:
            logger.warning(f"Colunas esperadas ausentes na Silver: {missing_cols}")
        else:
            logger.info("Todas as colunas esperadas estão presentes na Silver.")

        total = df.count()
        logger.info(f"Total de registros na Silver ({processing_date}): {total}")

        logger.info("Verificação OK: verify_silver.py")

    except Exception as e:
        logger.error(f"Erro no pipeline Silver: {e}")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
