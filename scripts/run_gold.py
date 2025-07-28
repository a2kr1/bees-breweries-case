from datetime import datetime
import os
from pathlib import Path
from pyspark.sql.functions import col, current_timestamp
from src.transform import (
    create_spark_session,
    write_delta,
)
from src.logger import logger

def main():
    try:
        spark = create_spark_session("GoldTransformation")

        base_silver = "/home/project/data/silver"
        base_gold = "/home/project/data/gold"
        table_name = "gold_breweries"

        carga = os.getenv("CARGA", "append").lower()
        logger.info(f"⚙️ Modo de carga: {carga}")

        datas_disponiveis = sorted([
            p.name.split("=")[-1] for p in Path(base_silver).iterdir()
            if p.is_dir() and "processing_date=" in p.name
        ])

        logger.info(f"📅 Datas de processamento Gold: {datas_disponiveis}")

        if not datas_disponiveis:
            raise ValueError("❌ Nenhuma data de partição disponível para a camada Gold.")

        df = (
            spark.read.format("delta").load(base_silver)
            .where(col("processing_date").isin(datas_disponiveis))
        )

        df_agg = (
            df.groupBy("state", "brewery_type", "processing_date")
            .count()
            .withColumnRenamed("count", "brewery_count")
            .withColumn("gold_load_date", current_timestamp())
        )

        if carga == "full":
            spark.sql(f"DROP TABLE IF EXISTS {table_name}")
            logger.info("🧹 Tabela Gold removida para recriação (modo full)")

        write_delta(
            df_agg,
            base_gold,
            mode="overwrite" if carga == "full" else "append",
            partition_col="processing_date",
        )

        logger.info("💬 Adicionando comentários nas colunas da Gold")
        spark.sql(f"CREATE TABLE IF NOT EXISTS {table_name} USING DELTA LOCATION '{base_gold}'")
        spark.sql("ALTER TABLE gold_breweries ALTER COLUMN state COMMENT 'Estado da cervejaria'")
        spark.sql("ALTER TABLE gold_breweries ALTER COLUMN brewery_type COMMENT 'Tipo da cervejaria'")
        spark.sql("ALTER TABLE gold_breweries ALTER COLUMN brewery_count COMMENT 'Quantidade de cervejarias agrupadas'")
        spark.sql("ALTER TABLE gold_breweries ALTER COLUMN processing_date COMMENT 'Data da carga'")
        spark.sql("ALTER TABLE gold_breweries ALTER COLUMN gold_load_date COMMENT 'Timestamp Gold'")

        logger.info("💾 Dados gravados com sucesso")

    except Exception as e:
        logger.exception(f"❌ Erro no pipeline Gold: {e}")

if __name__ == "__main__":
    main()
