import os
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count
from src.logger import logger  # ✅ Usando o logger direto

def get_spark_session(app_name="Silver Transformation") -> SparkSession:
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()
    return spark

def run_silver_transformation(spark: SparkSession, processing_date: str, delta_days: int) -> None:
    base_path = "/home/project/data"
    bronze_path = os.path.join(base_path, "bronze")
    silver_path = os.path.join(base_path, "silver")

    processing_dt = datetime.strptime(processing_date, "%Y-%m-%d")

    for i in range(delta_days + 1):
        current_date = processing_dt - timedelta(days=i)
        current_partition = current_date.strftime("%Y-%m-%d")
        current_input_dir = os.path.join(bronze_path, current_partition)
        current_output_dir = os.path.join(silver_path, f"processing_date={current_partition}")

        logger.info(f"🚀 Processando {current_partition}...")

        if not os.path.exists(current_input_dir):
            logger.warning(f"⚠️ Dados não encontrados para {current_partition}: {current_input_dir}")
            continue

        try:
            df = spark.read.option("multiLine", True).json(current_input_dir)

            if "_corrupt_record" in df.columns:
                total = df.count()
                corrupted = df.filter(col("_corrupt_record").isNotNull()).count()
                if total == corrupted:
                    logger.warning(f"❌ Todos os registros de {current_partition} estão corrompidos. Pulando.")
                    continue

            df_clean = df.dropDuplicates(["id"])

            df_clean.write.format("delta") \
                .mode("overwrite") \
                .option("overwriteSchema", "true") \
                .save(current_output_dir)

            logger.info(f"✅ Dados salvos em: {current_output_dir}")

        except Exception as e:
            logger.error(f"❌ Erro ao processar {current_partition}: {str(e)}")

    logger.info("✅ Reprocessamento finalizado.")

def run_gold_transformation(spark: SparkSession, processing_date: str) -> None:
    silver_path = "/home/project/data/silver"
    gold_path = "/home/project/data/gold"
    input_path = os.path.join(silver_path, f"processing_date={processing_date}")
    output_path = os.path.join(gold_path, f"processing_date={processing_date}")

    logger.info(f"🔄 Iniciando agregação Gold para {processing_date}...")

    if not os.path.exists(input_path):
        logger.warning(f"⚠️ Silver não encontrada para {processing_date}: {input_path}")
        return

    try:
        df = spark.read.format("delta").load(input_path)

        df_gold = df.groupBy("brewery_type", "state").agg(count("id").alias("total_breweries"))

        df_gold.write.format("delta") \
            .mode("overwrite") \
            .option("overwriteSchema", "true") \
            .save(output_path)

        logger.info(f"✅ Agregação Gold salva em: {output_path}")

    except Exception as e:
        logger.error(f"❌ Erro na transformação Gold: {str(e)}")
