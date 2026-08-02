from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 8, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def load_bulk_dump_task():
    print("Executing bulk loader step...")

def spark_clean_ratings_task():
    print("Executing PySpark ratings clean step...")

def spark_flatten_metadata_task():
    print("Executing PySpark metadata flatten step...")

with DAG(
    'anime_bulk_load_dag',
    default_args=default_args,
    description='One-time bulk historical load pipeline for static dump',
    schedule_interval=None,
    catchup=False,
) as dag:

    t_bulk = PythonOperator(
        task_id='load_bulk_dump',
        python_callable=load_bulk_dump_task,
    )

    t_spark_clean = PythonOperator(
        task_id='spark_clean_ratings',
        python_callable=spark_clean_ratings_task,
    )

    t_spark_flatten = PythonOperator(
        task_id='spark_flatten_metadata',
        python_callable=spark_flatten_metadata_task,
    )

    t_dbt_seed = BashOperator(
        task_id='dbt_seed',
        bash_command='cd /opt/airflow/warehouse && dbt seed',
    )

    t_dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/warehouse && dbt run',
    )

    t_dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /opt/airflow/warehouse && dbt test',
    )

    t_bulk >> t_spark_clean >> t_spark_flatten >> t_dbt_seed >> t_dbt_run >> t_dbt_test
