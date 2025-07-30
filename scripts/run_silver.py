import os
from datetime import datetime, timedelta
from pyspark.sql.functions import current_timestamp
from pyspark.sql.utils import AnalysisException

from src.transform import (
    create_spark_session,
    write_delta,
    list_available_dates,
    load_and_union_jsons,
    transform_to_silver
)
from src.utils import get_latest_date_folder, get_timezone_aware_date
from src.logger import logger


def extract_mode() -> str:
    return os.getenv("CARGA", "full").lower()


def extract_processing_dates(mode: str, base_path: str) -> list:
    if mode == "full":
        return list_available_dates(base_path)
    elif mode == "delta":
        days = int(os.getenv("DELTA_DAYS", "1"))
        return [
            (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(days)
        ]
    else:
        return [os.getenv("PROCESSING_DATE", get_timezone_aware_date())]


def create_table_if_not_exists(spark, path: str, recreate: bool = False):
    """
    Cria a tabela Delta da camada Silver com nome simples: silver_breweries.
    Essa nomenclatura evita conflitos com namespaces em catálogos locais.
    """
    table_name = "silver_breweries"

    if recreate:
        try:
            if spark.catalog.tableExists(table_name):
                spark.sql(f"DROP TABLE IF EXISTS {table_name}")
        except AnalysisException:
            pass

    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {table_name}
        USING DELTA
        LOCATION '{path}'
    """)

    if recreate:
        logger.info("Adicionando comentários nas colunas da Silver")
        spark.sql("ALTER TABLE silver_breweries ALTER COLUMN id COMMENT 'ID da cervejaria'")
        spark.sql("ALTER TABLE silver_breweries ALTER COLUMN name COMMENT 'Nome da cervejaria'")
        spark.sql("ALTER TABLE silver_breweries ALTER COLUMN state COMMENT 'Estado da cervejaria'")
        spark.sql("ALTER TABLE silver_breweries ALTER COLUMN brewery_type COMMENT 'Tipo de cervejaria'")
        spark.sql("ALTER TABLE silver_breweries ALTER COLUMN processing_date COMMENT 'Data da carga lógica'")
        spark.sql("ALTER TABLE silver_breweries ALTER COLUMN silver_load_date COMMENT 'Timestamp da carga Silver'")


def main():
    try:
        spark = create_spark_session("Silver Transformation")
        mode = extract_mode()
        logger.info(f"Modo de carga: {mode}")

        base_bronze = "/home/project/data/bronze"
        base_silver = "/home/project/data/silver"

        if mode == "full":
            latest_date = get_latest_date_folder(base_bronze)
            processing_dates = [latest_date]
        else:
            processing_dates = extract_processing_dates(mode, base_bronze)

        logger.info(f"Data de processamento da silver: {processing_dates}")

        input_path = os.path.join(base_bronze, processing_dates[0])

        for date in processing_dates:
            df_bronze = load_and_union_jsons(spark, input_path)
            df_silver = transform_to_silver(df_bronze, date)
            write_delta(df_silver, base_silver, mode="append", partition_col=["processing_date", "state"])

        create_table_if_not_exists(spark, base_silver, recreate=(mode == "full"))
        logger.info("Silver finalizada com sucesso.")
    except Exception as e:
        logger.error(f"Erro: {e}")
        raise


if __name__ == "__main__":
    main()
