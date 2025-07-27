# COMMAND ----------
# Imports
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, input_file_name
import os
from datetime import datetime

# COMMAND ----------
# Inicializa sessão Spark com Delta
spark = (
    SparkSession.builder
    .appName("Silver Layer - Breweries")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .getOrCreate()
)

# COMMAND ----------
# Parâmetros
processing_date = os.getenv("PROCESSING_DATE", datetime.today().strftime("%Y-%m-%d"))
input_path = f"/opt/landing/{processing_date}/*.json"
output_path = f"/opt/silver/breweries"

# COMMAND ----------
# Leitura dos dados JSON da camada Bronze
df = (
    spark.read.option("multiline", "true").json(input_path)
    .withColumn("processing_date", col("updated_at").substr(1, 10))
    .withColumn("source_file", input_file_name())
)

# COMMAND ----------
# Remove registros duplicados por id + updated_at
df_clean = (
    df.dropDuplicates(["id", "updated_at"])
)

# COMMAND ----------
# Enriquecimento de dados e seleção de colunas finais
df_final = (
    df_clean.select(
        "id",
        "name",
        "brewery_type",
        "city",
        "state",
        "country",
        "longitude",
        "latitude",
        "postal_code",
        "website_url",
        "updated_at",
        "processing_date"
    )
)

# COMMAND ----------
# Escrita no Delta Lake particionado por data de processamento
(
    df_final.write.format("delta")
    .mode("overwrite")
    .partitionBy("processing_date")
    .save(output_path)
)

# COMMAND ----------
# Finalização
print("✅ Transformação Silver concluída com sucesso.")
