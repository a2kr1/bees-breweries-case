import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from src.logger import setup_logger
from pathlib import Path
import json
from datetime import datetime

logger = setup_logger()

def read_bronze_json(spark, input_path: str):
    json_files = list(Path(input_path).glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"Nenhum arquivo JSON encontrado em {input_path}")

    try:
        df = spark.read.option("multiline", "true").json(str(input_path))
        return df
    except Exception as e:
        raise RuntimeError(f"Erro ao ler os arquivos JSON na Bronze: {e}")

def main():
    processing_date = os.getenv("PROCESSING_DATE")
    if not processing_date:
        processing_date = datetime.now().strftime("%Y-%m-%d")
        logger.info(f"PROCESSING_DATE não definido. Usando data atual: {processing_date}")

    logger.info(f"Verificando Bronze para PROCESSING_DATE = {processing_date}")

    spark = SparkSession.builder \
        .appName("Verify Bronze") \
        .getOrCreate()

    input_path = f"/home/project/data/bronze/{processing_date}"

    try:
        df = read_bronze_json(spark, input_path)

        # Verificar colunas esperadas
        expected_columns = ['id', 'name', 'brewery_type', 'state']
        missing_cols = [col for col in expected_columns if col not in df.columns]
        if missing_cols:
            logger.warning(f"Colunas esperadas ausentes na Bronze: {missing_cols}")
        else:
            logger.info("Todas as colunas esperadas estão presentes na Bronze.")

        # Verificar duplicatas pela coluna 'id'
        duplicates = df.groupBy("id").count().filter(col("count") > 1)
        num_duplicates = duplicates.count()
        if num_duplicates > 0:
            logger.warning(f"Encontradas {num_duplicates} duplicatas na Bronze.")
            duplicates.show(truncate=False)
        else:
            logger.info("Nenhuma duplicata encontrada na Bronze.")

        logger.info(f"Total de registros na Bronze: {df.count()}")
        logger.info("Verificação OK: verify_bronze.py")

    except Exception as e:
        logger.error(f"Erro no pipeline Bronze: {e}")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
