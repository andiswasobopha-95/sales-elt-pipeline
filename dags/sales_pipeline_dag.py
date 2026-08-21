"""
Airflow DAG: sales_elt_pipeline

extract_products  ->  load_to_postgres  ->  dbt_run  ->  dbt_test

Runs daily. Each task is a thin wrapper around the same scripts you can
run locally (see Makefile), so local runs and Airflow runs stay in sync.
"""
   from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "data-eng",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def _extract():
    from src.extract.extract_api import run as extract_run

    extract_run()


def _load():
    from src.load.load_to_postgres import run as load_run

    load_run()


with DAG(
    dag_id="sales_elt_pipeline",
    description="Extract product data, load with synthetic orders, transform with dbt",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    tags=["portfolio", "elt", "dbt"],
) as dag:

    extract_products = PythonOperator(
        task_id="extract_products",
        python_callable=_extract,
    )

    load_to_postgres = PythonOperator(
        task_id="load_to_postgres",
        python_callable=_load,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            "cd /opt/airflow/dbt_project && "
            "dbt run --profiles-dir /opt/airflow/dbt_project"
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            "cd /opt/airflow/dbt_project && "
            "dbt test --profiles-dir /opt/airflow/dbt_project"
        ),
    )

    extract_products >> load_to_postgres >> dbt_run >> dbt_test
