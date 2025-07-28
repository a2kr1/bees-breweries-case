import os
from pathlib import Path
from typing import Optional, List
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import current_timestamp, lit
from delta import configure_spark_with_delta_pip
from src.logger import logger
from functools import reduce


def create_spark_session(app_name: str = "BreweriesETL") -> SparkSession:
    builder = (
        SparkSession.builder
        .appName(app_name)
        .config("spark.jars.packages", os.getenv("DELTA_PACKAGE", "io.delta:delta-core_2.12:2.4.0"))
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.databricks.delta.schema.autoMerge.enabled", "true")
        .config("spark.sql.shuffle.partitions", "2")
    )
    return configure_spark_with_delta_pip(builder).getOrCreate()


def write_delta(
    df: DataFrame,
    output_path: str,
    mode: str = "append",
    partition_col: Optional[str] = None,
    overwrite_schema: bool = False
):
    writer = df.write.format("delta").mode(mode)
    if partition_col:
        writer = writer.partitionBy(partition_col)
    writer = writer.option("mergeSchema", "true")
    if overwrite_schema:
        writer = writer.option("overwriteSchema", "true")
    writer.save(output_path)


def list_available_dates(base_path: str) -> List[str]:
    path = Path(base_path)
    if not path.exists():
        return []
    return sorted([p.name for p in path.iterdir() if p.is_dir()])


def load_and_union_jsons(spark: SparkSession, input_path: str) -> DataFrame:
    """
    Lê múltiplos arquivos JSON paginados com múltiplos objetos por arquivo,
    unificando todos em um único DataFrame com tolerância a colunas ausentes.
    """
    files = sorted(Path(input_path).glob("*.json"))
    if not files:
        raise FileNotFoundError(f"Nenhum arquivo JSON encontrado em {input_path}")

    logger.info(f"📂 {len(files)} arquivos JSON encontrados para leitura")

    df_list = [
        spark.read.option("multiline", "true").json(str(file))
        for file in files
    ]

    if len(df_list) == 1:
        return df_list[0]

    df_union = reduce(lambda df1, df2: df1.unionByName(df2, allowMissingColumns=True), df_list)
    return df_union


def read_delta_partitioned(spark: SparkSession, path: str, partition_values: List[str]) -> DataFrame:
    """
    Lê dados particionados de um diretório Delta Lake com base em valores de partição.
    """
    all_dfs = []
    for date in partition_values:
        partition_path = os.path.join(path, f"processing_date={date}")
        if os.path.exists(partition_path) or _path_exists_on_hdfs(spark, partition_path):
            df = spark.read.format("delta").load(partition_path)
            all_dfs.append(df)
        else:
            logger.warning(f"⚠️ Partição não encontrada: {partition_path}")

    if not all_dfs:
        raise ValueError("❌ Nenhuma partição válida encontrada para leitura.")

    logger.info(f"📊 {len(all_dfs)} partições lidas com sucesso.")
    return reduce(lambda df1, df2: df1.unionByName(df2, allowMissingColumns=True), all_dfs)


def _path_exists_on_hdfs(spark: SparkSession, path: str) -> bool:
    """
    Verifica se um caminho existe no HDFS ou no sistema de arquivos distribuído acessível pelo Spark.
    """
    try:
        fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
        return fs.exists(spark._jvm.org.apache.hadoop.fs.Path(path))
    except Exception as e:
        logger.warning(f"⚠️ Erro ao verificar existência do caminho no HDFS: {e}")
        return False
