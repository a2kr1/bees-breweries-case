import os
import sys
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.utils import AnalysisException
from delta import configure_spark_with_delta_pip
from src.logger import setup_logger

logger = setup_logger()

builder = (
    SparkSession.builder.appName("VerifyGold")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
)
spark = configure_spark_with_delta_pip(builder).getOrCreate()

processing_date = os.getenv("PROCESSING_DATE")
if not processing_date:
    logger.error("Variável de ambiente PROCESSING_DATE não definida.")
    sys.exit(1)

logger.info(f"Verificando a tabela Gold")

base_dir = Path(__file__).resolve().parents[1]
gold_path = base_dir / "data" / "gold"

if not gold_path.exists():
    logger.error(f"Diretório não encontrado: {gold_path}")
    sys.exit(1)

try:
    df = spark.read.format("delta").load(str(gold_path)).where(f"processing_date = '{processing_date}'")
    logger.info("Leitura do Delta Lake na camada Gold realizada com sucesso.")

    df.printSchema()
    df.show(5, truncate=False)

    count = df.count()
    logger.info(f"Total de registros na Gold ({processing_date}): {count}")

except AnalysisException as e:
    logger.error(f"Erro ao ler Delta Lake Gold: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Erro inesperado: {e}")
    sys.exit(1)
finally:
    try:
        spark.stop()
    except NameError:
        pass
