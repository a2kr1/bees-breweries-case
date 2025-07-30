import os
from datetime import datetime, timedelta
from pyspark.sql import functions as F

from src.transform import (
    create_spark_session,
    write_delta
)
from src.utils import get_timezone_aware_date
from src.logger import logger


def extract_mode() -> str:
    return os.getenv("CARGA", "full").lower()


def extract_processing_dates(mode: str) -> list:
    base_silver = "/home/project/data/silver"

    if mode == "full":
        return sorted([
            name.split("=")[1]
            for name in os.listdir(base_silver)
            if os.path.isdir(os.path.join(base_silver, name)) and name.startswith("processing_date=")
        ])
    elif mode == "delta":
        days = int(os.getenv("DELTA_DAYS", "1"))
        return [
            (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(days)
        ]
    else:
        return [os.getenv("PROCESSING_DATE", get_timezone_aware_date())]


def main():
    try:
        spark = create_spark_session("Gold Aggregation")
        mode = extract_mode()
        logger.info(f"Modo de carga: {mode}")

        base_silver = "/home/project/data/silver"
        base_gold = "/home/project/data/gold"
        processing_dates = extract_processing_dates(mode)
        logger.info("[INFO] Lendo a tabela da Silver com filtro lógico por processing_date")

        df_silver = spark.read.format("delta").load(base_silver).where(F.col("processing_date").isin(processing_dates))

        required_columns = {"state", "brewery_type"}
        if not required_columns.issubset(set(df_silver.columns)):
            raise ValueError("Colunas necessárias ausentes na Silver: state, brewery_type")

        df_gold = df_silver.groupBy("state", "brewery_type").agg(
            F.count("*").alias("brewery_count")
        ).withColumn("processing_date", F.lit(get_timezone_aware_date())) \
         .withColumn("gold_load_date", F.current_timestamp())

        write_delta(df_gold, base_gold, mode="append", partition_col="processing_date")

        table_name = "gold_breweries"
        if mode == "full":
            spark.sql(f"DROP TABLE IF EXISTS {table_name}")

        spark.sql(f"""
            CREATE TABLE IF NOT EXISTS {table_name}
            USING DELTA
            LOCATION '{base_gold}'
        """)

        if mode == "full":
            logger.info("Adicionando comentários nas colunas da Gold")
            spark.sql("ALTER TABLE gold_breweries ALTER COLUMN state COMMENT 'Estado da cervejaria'")
            spark.sql("ALTER TABLE gold_breweries ALTER COLUMN brewery_type COMMENT 'Tipo de cervejaria'")
            spark.sql("ALTER TABLE gold_breweries ALTER COLUMN brewery_count COMMENT 'Quantidade de cervejarias agrupadas'")
            spark.sql("ALTER TABLE gold_breweries ALTER COLUMN processing_date COMMENT 'Data da carga lógica'")
            spark.sql("ALTER TABLE gold_breweries ALTER COLUMN gold_load_date COMMENT 'Timestamp da carga Gold'")

        logger.info("Gold finalizada com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao executar a Gold: {e}")
        raise


if __name__ == "__main__":
    main()
