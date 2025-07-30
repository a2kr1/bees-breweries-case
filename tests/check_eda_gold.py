from pyspark.sql import SparkSession
from pyspark.sql.functions import count, isnull, isnan, when, lit
from src.utils import get_timezone_aware_date  # ✅ Correção do import
from src.transform import create_spark_session

def main():
    processing_date = get_timezone_aware_date()  # ✅ Correção aqui
    spark = create_spark_session()

    print(f"[INFO] [EDA] Lendo dados da Gold para {processing_date}...")

    try:
        gold_path = f"/home/project/data/gold"
        df = (
            spark.read.format("delta")
            .load(gold_path)
            .where(f"processing_date = '{processing_date}'")
        )
        df.show(10)

        print("[INFO] Verificando campos nulos:")
        null_counts = df.select([
            count(
                when(
                    isnull(c) | (isnan(c) if dict(df.dtypes)[c] in ["double", "float"] else lit(False)),
                    c
                )
            ).alias(c)
            for c in df.columns
        ])
        null_counts.show()

    except Exception as e:
        print(f"[ERROR] Erro ao ler dados Silver: {e}")

if __name__ == "__main__":
    main()
