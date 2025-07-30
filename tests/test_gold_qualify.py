import pytest
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

@pytest.fixture(scope="module")
def spark():
    return SparkSession.builder \
        .appName("TestGold") \
        .master("local[1]") \
        .getOrCreate()

def test_gold_aggregation_columns(spark):
    df = spark.read.format("delta").load("/home/project/data/gold")

    expected_columns = {"state", "brewery_type", "brewery_count", "processing_date", "gold_load_date"}
    actual_columns = set(df.columns)

    assert expected_columns.issubset(actual_columns), f"Colunas esperadas ausentes: {expected_columns - actual_columns}"

def test_gold_grouping_uniqueness(spark):
    df = spark.read.format("delta").load("/home/project/data/gold")

    duplicates = df.groupBy("state", "brewery_type", "processing_date") \
                   .count() \
                   .filter(col("count") > 1)

    assert duplicates.count() == 0, "Encontradas duplicatas na Gold por state, brewery_type e processing_date"
