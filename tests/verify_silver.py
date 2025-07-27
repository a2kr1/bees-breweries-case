import sys
import os
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count

def get_processing_date():
    return os.getenv("PROCESSING_DATE", datetime.today().strftime("%Y-%m-%d"))

def verify_silver_layer(spark, path, primary_key=None):
    print(f"🔍 Verificando diretório: {path}")

    if not os.path.exists(path):
        print(f"❌ Diretório não encontrado: {path}")
        return

    delta_log = os.path.join(path, "_delta_log")
    if not os.path.exists(delta_log):
        print(f"❌ _delta_log ausente. A pasta não parece ser uma tabela Delta válida.")
        return

    try:
        df = spark.read.format("delta").load(path)
        record_count = df.count()
        print(f"✅ Dados carregados com sucesso. Registros: {record_count}")

        if record_count == 0:
            print("⚠️ Nenhum dado foi encontrado na camada Silver.")

        if primary_key:
            dup_df = df.groupBy(primary_key).agg(count("*").alias("dup_count")).filter(col("dup_count") > 1)
            dup_count = dup_df.count()
            if dup_count > 0:
                print(f"❌ Encontradas {dup_count} duplicatas com base na chave '{primary_key}'")
                dup_df.show(truncate=False)
            else:
                print(f"✅ Nenhuma duplicata encontrada com base na chave '{primary_key}'.")

    except Exception as e:
        print(f"❌ Erro ao ler a camada Silver: {e}")


if __name__ == "__main__":
    processing_date = get_processing_date()
    silver_path = f"/home/project/data/silver/{processing_date}"

    primary_key = "id"  # Confirmado como chave primária pela documentação

    spark = (
        SparkSession.builder
        .appName("Verify Silver Layer")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.sql.debug.maxToStringFields", 2000)
        .config("spark.jars.packages", "io.delta:delta-core_2.12:2.3.0")
        .getOrCreate()
    )

    verify_silver_layer(spark, silver_path, primary_key)
