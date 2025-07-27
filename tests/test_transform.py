
import pytest
from pyspark.sql import SparkSession
from src.transform import deduplicate_breweries

@pytest.fixture(scope="session")
def spark():
    return (
        SparkSession.builder.master("local[1]").appName("TestTransform").getOrCreate()
    )

def test_deduplicate_breweries(spark):
    data = [
        {"id": "a", "name": "Brew 1"},
        {"id": "a", "name": "Brew 1"},  # duplicata
        {"id": "b", "name": "Brew 2"}
    ]
    df = spark.createDataFrame(data)
    result = deduplicate_breweries(df)
    assert result.count() == 2
    ids = [row["id"] for row in result.collect()]
    assert set(ids) == {"a", "b"}
