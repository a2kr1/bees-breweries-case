
import os
from datetime import datetime, timedelta
from pyspark.sql.functions import current_timestamp
from src.transform import create_spark_session, write_delta, list_available_dates, load_and_union_jsons
from src.logger import logger
from pyspark.sql import functions as F
from pyspark.sql.utils import AnalysisException

def extract_mode() -> str:
    return os.getenv("CARGA", "append").lower()

def extract_processing_dates(mode: str, base_path: str) -> list:
    if mode == "full":
        return list_available_dates(base_path)
    elif mode == "delta":
        days = int(os.getenv("DELTA_DAYS", "1"))
        return [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
    else:
        return [os.getenv("PROCESSING_DATE", datetime.now().strftime("%Y-%m-%d"))]

def create_table_if_not_exists(spark, path: str, recreate: bool = False):
    full_table_name = "silver_breweries"
    if recreate:
        try:
            if spark.catalog.tableExists(full_table_name):
                spark.sql(f"DROP TABLE {full_table_name}")
        except AnalysisException:
            pass

    spark.sql(f'''
        CREATE TABLE IF NOT EXISTS {full_table_name}
        USING DELTA
        LOCATION '{path}'
    ''')

    if recreate:
        logger.info("💬 Adicionando comentários nas colunas da Silver")
        spark.sql("ALTER TABLE silver_breweries ALTER COLUMN id COMMENT 'ID da cervejaria'")
        spark.sql("ALTER TABLE silver_breweries ALTER COLUMN name COMMENT 'Nome da cervejaria'")
        spark.sql("ALTER TABLE silver_breweries ALTER COLUMN state COMMENT 'Estado'")
        spark.sql("ALTER TABLE silver_breweries ALTER COLUMN brewery_type COMMENT 'Tipo'")
        spark.sql("ALTER TABLE silver_breweries ALTER COLUMN processing_date COMMENT 'Data da carga'")
        spark.sql("ALTER TABLE silver_breweries ALTER COLUMN silver_load_date COMMENT 'Timestamp Silver'")

def main():
    try:
        spark = create_spark_session("SilverTransformation")
        mode = extract_mode()
        logger.info(f"⚙️ Modo de carga: {mode}")

        base_bronze = "/home/project/data/bronze"
        base_silver = "/home/project/data/silver"
        processing_dates = extract_processing_dates(mode, base_bronze)
        logger.info(f"📅 Datas de processamento Silver: {processing_dates}")

        for date in processing_dates:
            input_path = f"{base_bronze}/{date}"
            df = load_and_union_jsons(spark, input_path)
            df = df.select("id", "name", "state", "brewery_type") \
                   .withColumn("processing_date", F.lit(date)) \
                   .withColumn("silver_load_date", current_timestamp())

            write_delta(df, base_silver, mode="append", partition_col=["processing_date", "state"])

        create_table_if_not_exists(spark, base_silver, recreate=(mode == "full"))
        logger.info("💾 Dados gravados com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro no pipeline Silver: {str(e)}")
        raise

if __name__ == "__main__":
    main()
