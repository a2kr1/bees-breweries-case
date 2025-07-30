import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, isnan, isnull, when, lit
from datetime import datetime
from src.utils import get_timezone_aware_date
from src.logger import logger
from pyspark.sql.types import DoubleType, FloatType

def main():
    base_path = "/home/project/data/silver"

    # Obtém a data de processamento
    processing_date = os.getenv("PROCESSING_DATE")
    if not processing_date:
        processing_date = get_timezone_aware_date()
        logger.info(f"PROCESSING_DATE não definido. Usando data atual: {processing_date}")

    logger.info(f"Lendo dados da camada Silver para o processamento {processing_date}...")

    try:
        spark = (
            SparkSession.builder.appName("EDA Silver")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            .getOrCreate()
        )

        df = (
            spark.read.format("delta")
            .load(base_path)
            .where(col("processing_date") == processing_date)
        )

        logger.info("Leitura do Delta Lake na camada Silver realizada com sucesso.")
        df.printSchema()
        df.show(5, truncate=False)

        logger.info("Contagem total de registros:")
        logger.info(f"{df.count()} registros")

        logger.info("Distribuição por estado:")
        df.groupBy("state").count().orderBy("count", ascending=False).show(10, truncate=False)

        logger.info("Distribuição por tipo de cervejaria:")
        df.groupBy("brewery_type").count().orderBy("count", ascending=False).show(10, truncate=False)

        logger.info("Verificando campos nulos:")
        null_counts = df.select([
            count(
                when(
                    isnull(col(c)) | (isnan(col(c)) if dict(df.dtypes)[c] in ["double", "float"] else lit(False)),
                    c
                )
            ).alias(c)
            for c in df.columns
        ])
        null_counts.show()

    except Exception as e:
        logger.error(f"Erro ao ler dados da Silver: {e}")
        raise

if __name__ == "__main__":
    main()