# tests/test_transform.py

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType
from src.transform import transform_to_silver

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder \
        .appName("TestTransform") \
        .master("local[1]") \
        .getOrCreate()

def test_transform_to_silver_should_clean_and_add_metadata(spark):
    # Dado: um DataFrame bruto simulado como na camada Bronze
    input_data = [
        {"id": "abc123", "name": "Brew 1", "state": "Texas", "brewery_type": "micro"},
        {"id": "def456", "name": "Brew 2", "state": "California", "brewery_type": "regional"},
    ]
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("name", StringType(), True),
        StructField("state", StringType(), True),
        StructField("brewery_type", StringType(), True)
    ])
    df_input = spark.createDataFrame(input_data, schema=schema)

    # Quando: aplicamos a transformação
    processing_date = "2025-07-27"
    df_result = transform_to_silver(df_input, processing_date)

    # Então: o resultado deve conter as colunas esperadas e os campos de metadados
    expected_columns = {"id", "name", "state", "brewery_type", "silver_load_date", "processing_date"}
    assert expected_columns.issubset(set(df_result.columns))

    rows = df_result.collect()
    assert all(row["processing_date"] == processing_date for row in rows)
    assert all(row["silver_load_date"] is not None for row in rows)