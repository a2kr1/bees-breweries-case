from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "bees_data_engineer",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=3),
}

with DAG(
    dag_id="brewery_etl_pipeline",
    default_args=default_args,
    description="Pipeline ETL com Bronze, Silver e Gold para Open Brewery DB",
    schedule_interval=None,
    start_date=datetime(2025, 7, 28),
    catchup=False,
    tags=["bees", "etl", "delta"],
) as dag:

    run_bronze = BashOperator(
        task_id="bronze_etl",
        bash_command=(
            "docker exec -e PROCESSING_DATE={{ ds }} spark-container "
            "python3 /home/project/scripts/run_bronze.py"
        ),
    )

    run_silver = BashOperator(
        task_id="silver_etl",
        bash_command=(
            "docker exec -e PROCESSING_DATE={{ ds }} -e CARGA=delta -e DELTA_DAYS=2 "
            "-e PYTHONPATH=/home/project spark-container "
            "python3 /home/project/scripts/run_silver.py"
        ),
    )

    run_gold = BashOperator(
        task_id="gold_etl",
        bash_command=(
            "docker exec -e PROCESSING_DATE={{ ds }} -e CARGA=delta -e DELTA_DAYS=2 "
            "-e PYTHONPATH=/home/project spark-container "
            "python3 /home/project/scripts/run_gold.py"
        ),
    )

    run_verify = BashOperator(
        task_id="run_verifications",
        bash_command=(
            "docker exec -e PYTHONPATH=/home/project -e PROCESSING_DATE={{ ds }} "
            "spark-container python3 /home/project/tests/verify_all.py"
        ),
    )

    # Definindo as dependências entre as etapas do pipeline
    run_bronze >> run_silver >> run_gold >> run_verify
