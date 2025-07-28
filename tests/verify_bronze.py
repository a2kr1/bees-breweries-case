import sys
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, lit
from delta import configure_spark_with_delta_pip
from src.logger import logger
from src.transform import create_spark_session, write_delta, list_available_dates


def get_processing_dates(carga: str, ref_date: str, delta_days: int) -> list:
    tz = ZoneInfo("America/Sao_Paulo")
    today = datetime.now(tz).date()
    if carga == "full":
        base_path = Path(__file__).resolve().parents[1] / "data" / "bronze"
        return list_available_dates(str(base_path))
    elif carga == "delta":
        return [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta_days)]
    elif carga == "append":
        return [ref_date]
    else:
        logger.error(f"❌ Modo de carga inválido: {carga}")
        sys.exit(1)


def create_table_if_not_exists(spark: SparkSession, path: str, recreate: bool = False):
    table_name = "silver_breweries"
    if recreate and spark.catalog.tableExists(table_name):
        spark.sql(f"DROP TABLE {table_name}")

    delta_log_path = Path(path) / "_delta_log"
    if not delta_log_path.exists():
        logger.error(f"❌ Sem _delta_log em {path}. Silver não criada.")
        return

    if not spark.catalog.tableExists(table_name):
        spark.sql(f"""
            CREATE TABLE {table_name}
            USING DELTA
            LOCATION '{path}'
        """)
        spark.sql(f"ALTER TABLE {table_name} ALTER COLUMN id COMMENT 'Identificador único da cervejaria'")
        spark.sql(f"ALTER TABLE {table_name} ALTER COLUMN name COMMENT 'Nome da cervejaria'")
        spark.sql(f"ALTER TABLE {table_name} ALTER COLUMN state COMMENT 'Estado da cervejaria'")
        spark.sql(f"ALTER TABLE {table_name} ALTER COLUMN brewery_type COMMENT 'Tipo da cervejaria'")
        spark.sql(f"ALTER TABLE {table_name} ALTER COLUMN processing_date COMMENT 'Data do processamento diário'")
        spark.sql(f"ALTER TABLE {table_name} ALTER COLUMN silver_load_date COMMENT 'Timestamp da carga na Silver'")


if __name__ == "__main__":
    try:
        spark = create_spark_session("SilverTransformation")
        carga = os.getenv("CARGA", "append").lower()
        ref_date = os.getenv("PROCESSING_DATE")
        delta_days = int(os.getenv("DELTA_DAYS", "1"))

        tz = ZoneInfo("America/Sao_Paulo")
        if not ref_date:
            ref_date = datetime.now(tz).strftime("%Y-%m-%d")

        processing_dates = get_processing_dates(carga, ref_date, delta_days)
        logger.info(f"📅 Datas de processamento Silver: {processing_dates}")

        base_dir = Path(__file__).resolve().parents[1]
        bronze_base_path = base_dir / "data" / "bronze"
        silver_base_path = base_dir / "data" / "silver"

        for date in processing_dates:
            bronze_input_path = str(bronze_base_path / date)
            df = spark.read.option("multiline", "true").json(f"{bronze_input_path}/*.json")
            df_transformed = df.dropDuplicates(["id", "processing_date"])
            df_transformed = df_transformed.withColumn("silver_load_date", current_timestamp())
            df_final = df_transformed.withColumn("processing_date", lit(date))

            write_delta(df_final, str(silver_base_path), mode="overwrite" if carga == "full" else "append", partition_col=["processing_date", "state"], overwrite_schema=(carga == "full"))

        create_table_if_not_exists(spark, str(silver_base_path), recreate=(carga == "full"))
        logger.info("✅ Pipeline Silver finalizada com sucesso.")

    except Exception as e:
        logger.exception(f"❌ Erro no pipeline Silver: {e}")
        sys.exit(1)
    finally:
        try:
            spark.stop()
        except NameError:
            pass
